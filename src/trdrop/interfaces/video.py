"""VideoReader interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np


class VideoReader(ABC):
    """
    Abstract interface for video frame reading.

    Frames are always read into caller-provided buffers.
    The reader maintains no frame data - only decoding state.
    """

    @property
    @abstractmethod
    def path(self) -> Path:
        """Source video file path."""

    @property
    @abstractmethod
    def fps(self) -> float:
        """Container framerate."""

    @property
    @abstractmethod
    def width(self) -> int:
        """Frame width in pixels."""

    @property
    @abstractmethod
    def height(self) -> int:
        """Frame height in pixels."""

    @property
    @abstractmethod
    def total_frames(self) -> int:
        """Total frame count (may be estimated)."""

    @property
    def frame_shape(self) -> tuple[int, int, int]:
        """Expected buffer shape: (height, width, 3)."""
        return (self.height, self.width, 3)

    @abstractmethod
    def read(self, out: np.ndarray) -> bool:
        """
        Read next frame into buffer.

        Args:
            out: Pre-allocated buffer, shape (height, width, 3), dtype uint8.

        Returns:
            True if frame was read, False if end of video.
        """

    @abstractmethod
    def seek(self, frame_index: int) -> None:
        """Seek to frame index."""

    @abstractmethod
    def close(self) -> None:
        """Release resources."""

    def __enter__(self) -> VideoReader:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
