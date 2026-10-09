"""Video reader implementations."""

from __future__ import annotations

import logging
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from trdrop.interfaces.video import VideoReader
from trdrop.profiling import get_profiler

logger = logging.getLogger(__name__)

_TRC_PQ = 16
_TRC_HLG = 18
_PRIM_BT709 = 1
_PRIM_BT2020 = 9


def _hdr_to_sdr(rgb: np.ndarray, transfer: int, primaries: int) -> np.ndarray:
    """Convert normalized PQ/HLG RGB to BT.709 SDR bytes."""
    if transfer == _TRC_PQ:
        # SMPTE ST 2084 EOTF: absolute luminance in nits.
        m1, m2 = 0.1593017578125, 78.84375
        c1, c2, c3 = 0.8359375, 18.8515625, 18.6875
        peak_nits = 10000.0
        t = np.power(np.maximum(rgb, 1e-10), 1.0 / m2)
        linear = peak_nits * np.power(
            np.maximum(t - c1, 0.0) / (c2 - c3 * t + 1e-10), 1.0 / m1,
        )
    elif transfer == _TRC_HLG:
        # BT.2100 inverse HLG OETF, followed by the reference display OOTF.
        # Use the nominal 1000-nit display (system gamma 1.2).
        a = 0.17883277
        b = 1.0 - 4.0 * a
        c = 0.5 - a * np.log(4.0 * a)
        scene = np.where(rgb <= 0.5, rgb * rgb / 3.0, (np.exp((rgb - c) / a) + b) / 12.0)
        weights = (
            [0.2126, 0.7152, 0.0722] if primaries == _PRIM_BT709
            else [0.2627, 0.6780, 0.0593]
        )
        luminance = np.sum(scene * weights, axis=-1, keepdims=True)
        peak_nits = 1000.0
        linear = peak_nits * scene * np.power(luminance, 0.2)
    else:
        raise ValueError(f"Unsupported HDR transfer: {transfer}")

    if primaries == _PRIM_BT2020:
        matrix = np.array([
            [1.6605, -0.5877, -0.0728],
            [-0.1246, 1.1329, -0.0083],
            [-0.0182, -0.1006, 1.1187],
        ])
        lin709 = np.einsum("ij,...j->...i", matrix, linear)
    else:
        lin709 = linear
    lin709 = np.maximum(lin709, 0.0)

    # Extended Reinhard tonemap, normalized to SDR reference white (100 nits)
    v = lin709 / 100.0
    white = peak_nits / 100.0
    mapped = v * (1.0 + v / (white * white)) / (1.0 + v)
    mapped = np.clip(mapped, 0.0, 1.0)

    # BT.709 OETF
    sdr = np.where(
        mapped < 0.018,
        mapped * 4.5,
        1.099 * np.power(np.maximum(mapped, 1e-10), 0.45) - 0.099,
    )
    return np.clip(sdr * 255.0, 0, 255).astype(np.uint8)


def _build_tonemap_lut3d(transfer: int, primaries: int) -> np.ndarray:
    """Build the 48 MiB LUT in slices to bound temporary memory usage."""
    lut = np.empty((256, 256, 256, 3), dtype=np.uint8)
    values = np.arange(256, dtype=np.float64) / 255.0
    rgb = np.empty((256, 256, 3), dtype=np.float64)
    rgb[..., 1] = values[:, None]
    rgb[..., 2] = values[None, :]
    for red in range(256):
        rgb[..., 0] = values[red]
        lut[red] = _hdr_to_sdr(rgb, transfer, primaries)
    return lut


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


_apply_lut3d = _get_lut3d_applier()


@lru_cache(maxsize=4)
def _get_tonemap_lut3d(transfer: int, primaries: int) -> np.ndarray:
    logger.info("Building HDR→SDR LUT (transfer=%s, primaries=%s)...", transfer, primaries)
    lut = _build_tonemap_lut3d(transfer, primaries)
    _apply_lut3d(np.zeros((1, 1, 3), dtype=np.uint8), lut)
    return lut


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
        self._tonemap_lut: np.ndarray | None = None
        self._color_key: tuple[int, int] | None = None
        self._seek_target_pts: int | None = None
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

        assert self._frame_iter is not None
        profiler = get_profiler()
        try:
            # Time the decode operation
            t0 = time.perf_counter()
            frame = next(self._frame_iter)
            # Container seeking lands on a preceding keyframe. Decode forward
            # to the requested frame instead of returning that keyframe.
            while (
                self._seek_target_pts is not None
                and frame.pts is not None
                and frame.pts < self._seek_target_pts
            ):
                frame = next(self._frame_iter)
            self._seek_target_pts = None

            # High bit depth and BT.2020 primaries are also valid for SDR.
            # Only PQ/HLG transfer metadata enables HDR conversion.
            ctx = self._stream.codec_context
            transfer = getattr(frame, "color_trc", ctx.color_trc)
            primaries = getattr(frame, "color_primaries", ctx.color_primaries)
            if transfer == 2:  # unspecified on frame: use stream metadata
                transfer = ctx.color_trc
            if primaries == 2:
                primaries = ctx.color_primaries
            key = (transfer, primaries)
            if key != self._color_key:
                self._hdr_tonemap = transfer in (_TRC_PQ, _TRC_HLG)
                self._tonemap_lut = None
                if self._hdr_tonemap:
                    gamut = _PRIM_BT709 if primaries == _PRIM_BT709 else _PRIM_BT2020
                    self._tonemap_lut = _get_tonemap_lut3d(transfer, gamut)
                self._color_key = key

            self._current_frame += 1
            # Copy frame data to output buffer
            arr = frame.to_ndarray(format="rgb24")

            if self._tonemap_lut is not None:
                arr = _apply_lut3d(arr, self._tonemap_lut)

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
        target_ts = (self._stream.start_time or 0) + int(frame_index / self._fps / time_base)

        self._container.seek(target_ts, stream=self._stream)
        self._frame_iter = None
        self._seek_target_pts = target_ts
        self._current_frame = frame_index - 1

    def close(self) -> None:
        """Close the video file."""
        self._container.close()
