"""Frame data types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np


class ReleaseCallback(ABC):
    """Interface for frame release notification."""

    @abstractmethod
    def __call__(self) -> None:
        """Called when the frame pair is no longer needed."""


class NoopRelease(ReleaseCallback):
    """Default no-op release for sources that don't need lifecycle management."""

    def __call__(self) -> None:
        pass


_NOOP_RELEASE = NoopRelease()


@dataclass(frozen=True, slots=True)
class FrameView:
    """
    Read-only view of frame data.

    The underlying buffer is owned elsewhere and may be reused
    after this view is released. Do not store references beyond
    the current iteration.
    """

    _data: np.ndarray
    index: int
    pts: int

    @property
    def array(self) -> np.ndarray:
        """Underlying array. DO NOT MODIFY."""
        return self._data

    @property
    def shape(self) -> tuple[int, int, int]:
        """Frame shape: (height, width, channels)."""
        return self._data.shape  # type: ignore[return-value]

    def to_owned(self) -> np.ndarray:
        """Create a copy that caller owns and can modify."""
        return self._data.copy()


@dataclass(frozen=True, slots=True)
class FramePair:
    """
    Two consecutive frames for comparison.

    Holds references to source-owned buffers. Call release() when done
    to signal that buffers can be recycled. Failure to release may cause
    the source to block or run out of buffers.
    """

    prev: FrameView
    curr: FrameView
    _on_release: ReleaseCallback = field(default=_NOOP_RELEASE, repr=False)

    @property
    def frame_index(self) -> int:
        """Index of the current (newer) frame."""
        return self.curr.index

    def release(self) -> None:
        """
        Signal that this pair is no longer needed.

        After calling release(), the underlying frame buffers may be
        recycled by the source. Do not access prev/curr after release.
        """
        self._on_release()
