"""Streaming video exporter using PyAV."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import av
import numpy as np

from trdrop.compositor.types import CompositorOutput
from trdrop.export.base import StreamingExporter


class StreamingVideoExporter(StreamingExporter):
    """Encodes composited frames to video file.

    Uses PyAV for encoding. Supports common codecs (h264, hevc, etc.).
    """

    def __init__(
        self,
        path: Path | str,
        fps: float,
        *,
        codec: str = "libx264",
        pix_fmt: str = "yuv420p",
        crf: int = 23,
        preset: str = "medium",
    ) -> None:
        self._path = Path(path)
        self._fps = fps
        self._codec = codec
        self._pix_fmt = pix_fmt
        self._crf = crf
        self._preset = preset

        self._container: av.container.OutputContainer | None = None
        self._stream: av.video.stream.VideoStream | None = None
        self._frame_count = 0

    def open(self) -> None:
        self._container = av.open(str(self._path), mode="w")
        # Stream created on first frame (need dimensions)
        self._stream = None
        self._frame_count = 0

    def write_frame(self, output: CompositorOutput) -> None:
        if self._container is None:
            raise RuntimeError("Exporter not opened")

        frame_data = output.frame
        height, width = frame_data.shape[:2]

        # Create stream on first frame
        if self._stream is None:
            # PyAV requires Fraction for rate
            fps_frac = Fraction(self._fps).limit_denominator(10000)
            self._stream = self._container.add_stream(self._codec, rate=fps_frac)
            self._stream.width = width
            self._stream.height = height
            self._stream.pix_fmt = self._pix_fmt
            self._stream.options = {
                "crf": str(self._crf),
                "preset": self._preset,
            }

        # Create PyAV frame from numpy array
        frame = av.VideoFrame.from_ndarray(frame_data, format="rgb24")
        frame.pts = self._frame_count

        # Encode and write
        for packet in self._stream.encode(frame):
            self._container.mux(packet)

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
