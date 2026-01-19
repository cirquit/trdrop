"""Video reader implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator, Protocol

import numpy as np


class VideoReader(Protocol):
    """Protocol for video reader implementations."""

    @property
    def path(self) -> Path: ...

    @property
    def fps(self) -> float: ...

    @property
    def width(self) -> int: ...

    @property
    def height(self) -> int: ...

    @property
    def total_frames(self) -> int: ...

    @property
    def current_frame(self) -> int: ...

    @property
    def current_pts(self) -> int: ...

    def seek(self, frame_index: int) -> None: ...

    def read(self) -> np.ndarray | None:
        """Read next frame. Returns RGB array or None at end."""
        ...

    def read_into(self, buffer: np.ndarray) -> bool:
        """Read next frame into pre-allocated buffer. Returns False at end."""
        ...

    def close(self) -> None: ...

    def __enter__(self) -> "VideoReader": ...

    def __exit__(self, *args: object) -> None: ...


class PyAVReader:
    """Video reader using PyAV (libav/ffmpeg bindings)."""

    def __init__(self, path: str | Path) -> None:
        import av

        self._path = Path(path)
        self._container: Any = av.open(str(path))
        self._stream: Any = self._container.streams.video[0]

        # Cache metadata
        self._fps = float(self._stream.average_rate or self._stream.base_rate or 30)
        self._width: int = self._stream.width
        self._height: int = self._stream.height
        self._total_frames: int = self._stream.frames or self._estimate_frames()

        # Iterator state
        self._frame_iter: Iterator[Any] | None = None
        self._current_frame = -1
        self._current_pts = 0

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

    @property
    def current_frame(self) -> int:
        return self._current_frame

    @property
    def current_pts(self) -> int:
        return self._current_pts

    def seek(self, frame_index: int) -> None:
        """Seek to specific frame. Discards current iterator."""
        if frame_index < 0:
            frame_index = 0

        # Convert frame index to timestamp
        time_base = float(self._stream.time_base)
        target_ts = int(frame_index / self._fps / time_base)

        self._container.seek(target_ts, stream=self._stream)
        self._frame_iter = None
        self._current_frame = frame_index - 1  # Will be incremented on next read

    def read(self) -> np.ndarray | None:
        """Read next frame as RGB numpy array."""
        if self._frame_iter is None:
            self._frame_iter = self._container.decode(video=0)

        assert self._frame_iter is not None
        try:
            frame = next(self._frame_iter)
            self._current_frame += 1
            self._current_pts = frame.pts or 0

            # Convert to RGB numpy array
            return frame.to_ndarray(format="rgb24")

        except StopIteration:
            return None

    def read_into(self, buffer: np.ndarray) -> bool:
        """Read next frame into pre-allocated buffer."""
        frame = self.read()
        if frame is None:
            return False

        np.copyto(buffer, frame)
        return True

    def close(self) -> None:
        """Close the video file."""
        self._container.close()

    def __enter__(self) -> "PyAVReader":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def __iter__(self) -> Iterator[np.ndarray]:
        """Iterate over all frames."""
        self.seek(0)
        while True:
            frame = self.read()
            if frame is None:
                break
            yield frame
