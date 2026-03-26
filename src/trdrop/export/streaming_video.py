"""Streaming video exporter using PyAV."""

from __future__ import annotations

import time
from fractions import Fraction
from pathlib import Path

import av  # type: ignore[import-untyped]

from trdrop.compositor.types import CompositorOutput
from trdrop.export.base import StreamingExporter
from trdrop.profiling import get_profiler

# Hardware encoder preference order (fastest/best quality first)
_HW_HEVC_PRIORITY = [
    "hevc_videotoolbox",  # macOS (Apple Silicon / Intel GPU)
    "hevc_nvenc",         # NVIDIA (Windows/Linux)
    "hevc_amf",           # AMD (Windows)
    "hevc_qsv",           # Intel QuickSync (Windows/Linux)
    "hevc_vaapi",         # Linux VAAPI
]

_HW_H264_PRIORITY = [
    "h264_videotoolbox",  # macOS (Apple Silicon / Intel GPU)
    "h264_nvenc",         # NVIDIA (Windows/Linux)
    "h264_amf",           # AMD (Windows)
    "h264_qsv",           # Intel QuickSync (Windows/Linux)
    "h264_vaapi",         # Linux VAAPI
]

_HW_ALL = set(_HW_HEVC_PRIORITY + _HW_H264_PRIORITY)

_SOFTWARE_HEVC = "libx265"
_SOFTWARE_H264 = "libx264"


_OPEN_ENCODER_CACHE: dict[str, bool] = {}


def _can_open_encoder(name: str) -> bool:
    """Test if an encoder can actually be constructed and opened on this hardware."""
    if name in _OPEN_ENCODER_CACHE:
        return _OPEN_ENCODER_CACHE[name]

    try:
        codec = av.Codec(name, "w")
        if not codec:
            _OPEN_ENCODER_CACHE[name] = False
            return False
        ctx = codec.create()
        ctx.open()
        _OPEN_ENCODER_CACHE[name] = True
        return True
    except Exception:
        _OPEN_ENCODER_CACHE[name] = False
        return False


def get_best_encoder() -> str:
    """Return best available encoder, preferring HEVC over H264.

    Tries HEVC hardware → H264 hardware → libx265 → libx264.
    """
    available = set(av.codecs_available)
    for enc in _HW_HEVC_PRIORITY:
        if enc in available and _can_open_encoder(enc):
            return enc
    for enc in _HW_H264_PRIORITY:
        if enc in available and _can_open_encoder(enc):
            return enc
    if _SOFTWARE_HEVC in available and _can_open_encoder(_SOFTWARE_HEVC):
        return _SOFTWARE_HEVC
    return _SOFTWARE_H264


def is_hardware_encoder(codec: str) -> bool:
    """Check if codec is a hardware encoder."""
    return codec in _HW_ALL


class StreamingVideoExporter(StreamingExporter):
    """Encodes composited frames to video file.

    Uses PyAV for encoding. Supports common codecs (h264, hevc, etc.).
    """

    def __init__(
        self,
        path: Path | str,
        fps: float,
        *,
        codec: str = "auto",
        pix_fmt: str = "yuv420p",
        crf: int = 23,
        preset: str = "medium",
        quality: int = 65,
    ) -> None:
        """Initialize video exporter.

        Args:
            path: Output file path.
            fps: Output framerate.
            codec: Video codec. Use "auto" for automatic hardware detection,
                or specify directly (libx264, h264_videotoolbox, h264_nvenc, etc.)
            pix_fmt: Pixel format (default yuv420p).
            crf: Quality for libx264 (0-51, lower=better, default 23).
            preset: Speed preset for libx264 (ultrafast to veryslow, default medium).
            quality: Quality for hardware encoders (0-100, higher=better, default 65).
        """
        self._path = Path(path)
        self._fps = fps
        self._pix_fmt = pix_fmt
        self._crf = crf
        self._preset = preset
        self._quality = quality

        # Resolve "auto" to best available encoder
        if codec == "auto":
            self._codec = get_best_encoder()
        else:
            self._codec = codec

        self._is_hw = is_hardware_encoder(self._codec)

        self._container: av.OutputContainer | None = None  # type: ignore[name-defined]
        self._stream: av.VideoStream | None = None  # type: ignore[name-defined]
        self._frame_count = 0

    def open(self) -> None:
        self._container = av.open(str(self._path), mode="w")
        # Stream created on first frame (need dimensions)
        self._stream = None
        self._frame_count = 0

    def write_frame(self, output: CompositorOutput) -> None:
        if self._container is None:
            raise RuntimeError("Exporter not opened")

        profiler = get_profiler()
        t_start = time.perf_counter()

        frame_data = output.frame
        height, width = frame_data.shape[:2]

        # Create stream on first frame
        if self._stream is None:
            # PyAV requires Fraction for rate
            fps_frac = Fraction(self._fps).limit_denominator(10000)
            stream = self._container.add_stream(self._codec, rate=fps_frac)
            stream.width = width
            stream.height = height
            stream.pix_fmt = self._pix_fmt

            # Mark output as BT.709 SDR so players don't misinterpret tonemapped content
            stream.codec_context.color_primaries = 1   # BT.709
            stream.codec_context.color_trc = 1         # BT.709
            stream.codec_context.colorspace = 1        # BT.709

            # Set encoder options (different for HW vs SW encoders)
            if self._is_hw:
                # Hardware encoders use quality-based settings
                stream.options = {"q:v": str(self._quality)}  # type: ignore[assignment]
            elif self._codec == "libx265":
                stream.options = {  # type: ignore[assignment]
                    "crf": str(self._crf),
                    "preset": self._preset,
                    "x265-params": "log-level=error",
                }
            else:
                # libx264
                stream.options = {  # type: ignore[assignment]
                    "crf": str(self._crf),
                    "preset": self._preset,
                }
            self._stream = stream

        # Create PyAV frame from numpy array
        t0 = time.perf_counter()
        frame = av.VideoFrame.from_ndarray(frame_data, format="rgb24")
        frame.pts = self._frame_count
        profiler.add_timing("export_video_convert", (time.perf_counter() - t0) * 1000)

        # Encode and write
        t0 = time.perf_counter()
        for packet in self._stream.encode(frame):  # type: ignore[union-attr]
            self._container.mux(packet)
        profiler.add_timing("export_video_encode", (time.perf_counter() - t0) * 1000)

        profiler.add_timing("export_video_total", (time.perf_counter() - t_start) * 1000)
        self._frame_count += 1

    def close(self) -> None:
        if self._container is not None:
            # Flush encoder
            if self._stream is not None:
                for packet in self._stream.encode():
                    self._container.mux(packet)
            self._container.close()
            self._container = None
            self._stream = None

    @property
    def path(self) -> Path:
        return self._path

    @property
    def codec(self) -> str:
        """Return the codec being used."""
        return self._codec

    @property
    def is_hardware_encoder(self) -> bool:
        """Return True if using hardware encoding."""
        return self._is_hw
