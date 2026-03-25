"""Video reader implementations."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Iterator

import logging

import numpy as np

from trdrop.interfaces.video import VideoReader
from trdrop.profiling import get_profiler

logger = logging.getLogger(__name__)


def _build_pq_tonemap_lut3d() -> np.ndarray:
    """Build a 256×256×256×3 LUT for full HDR→SDR conversion.

    Pipeline: PQ EOTF → BT.2020→BT.709 gamut mapping → Reinhard tonemap → BT.709 OETF.
    """
    # PQ EOTF constants (SMPTE ST 2084)
    m1 = 0.1593017578125
    m2 = 78.84375
    c1 = 0.8359375
    c2 = 18.8515625
    c3 = 18.6875

    # BT.2020 → BT.709 color matrix (ITU-R BT.2087)
    M = np.array([
        [1.6605, -0.5877, -0.0728],
        [-0.1246, 1.1329, -0.0083],
        [-0.0182, -0.1006, 1.1187],
    ], dtype=np.float64)

    idx = np.arange(256, dtype=np.float64) / 255.0
    r, g, b = np.meshgrid(idx, idx, idx, indexing="ij")
    rgb = np.stack([r, g, b], axis=-1)  # (256, 256, 256, 3)

    # PQ EOTF: normalized PQ signal → linear light (0–10000 nits)
    t = np.power(np.maximum(rgb, 1e-10), 1.0 / m2)
    linear = 10000.0 * np.power(
        np.maximum(t - c1, 0.0) / (c2 - c3 * t + 1e-10),
        1.0 / m1,
    )

    # BT.2020 → BT.709 gamut mapping in linear light
    lin709 = np.einsum("ij,...j->...i", M, linear)
    lin709 = np.maximum(lin709, 0.0)

    # Extended Reinhard tonemap, normalized to SDR reference white (100 nits)
    v = lin709 / 100.0
    Lw = 10000.0 / 100.0
    mapped = v * (1.0 + v / (Lw * Lw)) / (1.0 + v)
    mapped = np.clip(mapped, 0.0, 1.0)

    # BT.709 OETF
    sdr = np.where(
        mapped < 0.018,
        mapped * 4.5,
        1.099 * np.power(np.maximum(mapped, 1e-10), 0.45) - 0.099,
    )
    return np.clip(sdr * 255.0, 0, 255).astype(np.uint8)


def _get_lut3d_applier():
    """Return a fast 3D LUT apply function (numba-accelerated if available)."""
    try:
        import numba

        @numba.njit(parallel=True)
        def _apply(img, lut):
            h, w = img.shape[0], img.shape[1]
            out = np.empty_like(img)
            for y in numba.prange(h):
                for x in range(w):
                    r = img[y, x, 0]
                    g = img[y, x, 1]
                    b = img[y, x, 2]
                    out[y, x, 0] = lut[r, g, b, 0]
                    out[y, x, 1] = lut[r, g, b, 1]
                    out[y, x, 2] = lut[r, g, b, 2]
            return out

        return _apply
    except ImportError:
        def _apply(img, lut):
            return lut[img[..., 0], img[..., 1], img[..., 2]]
        return _apply


# Lazy-initialized globals (built on first HDR video encounter)
_pq_lut3d: np.ndarray | None = None
_apply_lut3d = _get_lut3d_applier()


def _ensure_pq_lut3d() -> np.ndarray:
    global _pq_lut3d
    if _pq_lut3d is None:
        logger.info("Building HDR→SDR 3D LUT (48MB, one-time cost)...")
        _pq_lut3d = _build_pq_tonemap_lut3d()
        # Warm up numba JIT with a tiny array
        tiny = np.zeros((1, 1, 3), dtype=np.uint8)
        _apply_lut3d(tiny, _pq_lut3d)
    return _pq_lut3d


class PyAVReader(VideoReader):
    """Video reader using PyAV (libav/ffmpeg bindings)."""

    def __init__(self, path: str | Path) -> None:
        import av

        self._path = Path(path)
        self._container: Any = av.open(str(path))
        self._stream: Any = self._container.streams.video[0]
        self._stream.thread_type = "AUTO"

        self._fps = float(self._stream.average_rate or self._stream.base_rate or 30)
        self._width: int = self._stream.width
        self._height: int = self._stream.height
        self._total_frames: int = self._stream.frames or self._estimate_frames()

        self._frame_iter: Iterator[Any] | None = None
        self._hdr_tonemap = False
        self._current_frame = -1

    def _estimate_frames(self) -> int:
        """Estimate frame count from duration if not available."""
        if self._stream.duration:
            time_base = float(self._stream.time_base)
            duration_sec = self._stream.duration * time_base
            return int(duration_sec * self._fps)
        return 0

    @property
    def path(self) -> Path:
        return self._path

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def total_frames(self) -> int:
        return self._total_frames

    def read(self, out: np.ndarray) -> bool:
        """Read next frame into buffer."""
        if out.shape != self.frame_shape or out.dtype != np.uint8:
            raise ValueError(
                f"Buffer must be {self.frame_shape} uint8, got {out.shape} {out.dtype}"
            )

        if self._frame_iter is None:
            self._frame_iter = self._container.decode(video=0)
            self._hdr_tonemap = False

            # Detect HDR via color transfer characteristic (integer enum from FFmpeg)
            # AVCOL_TRC_SMPTE2084 (PQ) = 16, AVCOL_TRC_ARIB_STD_B67 (HLG) = 18
            _TRC_PQ = 16
            _TRC_HLG = 18
            _PRIM_BT2020 = 9  # AVCOL_PRI_BT2020
            trc_val = getattr(self._stream.codec_context, "color_trc", None)
            prim_val = getattr(self._stream.codec_context, "color_primaries", None)
            pix_fmt = getattr(self._stream.codec_context, "pix_fmt", "") or ""
            is_hdr = (
                trc_val in (_TRC_PQ, _TRC_HLG)
                or prim_val == _PRIM_BT2020
                or "10le" in pix_fmt
                or "12le" in pix_fmt
            )

            if is_hdr:
                _ensure_pq_lut3d()
                self._hdr_tonemap = True
                logger.info("HDR detected (trc=%s, pix_fmt=%s). Tonemapping to SDR enabled.", trc_val, pix_fmt)

        assert self._frame_iter is not None
        profiler = get_profiler()
        try:
            # Time the decode operation
            t0 = time.perf_counter()
            frame = next(self._frame_iter)

            self._current_frame += 1
            # Copy frame data to output buffer
            arr = frame.to_ndarray(format="rgb24")

            if self._hdr_tonemap:
                arr = _apply_lut3d(arr, _pq_lut3d)

            np.copyto(out, arr)
            t1 = time.perf_counter()
            profiler.add_timing("read_decode", (t1 - t0) * 1000)
            return True
        except StopIteration:
            return False

    def seek(self, frame_index: int) -> None:
        """Seek to specific frame."""
        if frame_index < 0:
            frame_index = 0

        time_base = float(self._stream.time_base)
        target_ts = int(frame_index / self._fps / time_base)

        self._container.seek(target_ts, stream=self._stream)
        self._frame_iter = None
        self._current_frame = frame_index - 1

    def close(self) -> None:
        """Close the video file."""
        self._container.close()
