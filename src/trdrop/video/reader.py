"""Video reader implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

import numpy as np

from trdrop.interfaces.video import VideoReader


class PyAVReader(VideoReader):
    """Video reader using PyAV (libav/ffmpeg bindings)."""

    def __init__(self, path: str | Path) -> None:
        import av

        self._path = Path(path)
        self._container: Any = av.open(str(path))
        self._stream: Any = self._container.streams.video[0]

        self._fps = float(self._stream.average_rate or self._stream.base_rate or 30)
        self._width: int = self._stream.width
        self._height: int = self._stream.height
        self._total_frames: int = self._stream.frames or self._estimate_frames()

        self._frame_iter: Iterator[Any] | None = None
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
        try:
            frame = next(self._frame_iter)
            self._current_frame += 1
            # Copy frame data to output buffer
            arr = frame.to_ndarray(format="rgb24")
            np.copyto(out, arr)
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
