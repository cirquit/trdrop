"""Frame source interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from trdrop.types.frames import FramePair


class FrameSource(ABC):
    """
    Abstract source of FramePairs.

    Implementations handle:
    - Buffer allocation and lifecycle
    - Prefetching strategy (or none)
    - Frame pairing (prev, curr)

    Consumers receive read-only FramePairs and must not
    retain references after iteration advances.
    """

    @property
    @abstractmethod
    def fps(self) -> float:
        """Container framerate."""

    @property
    @abstractmethod
    def total_frames(self) -> int:
        """Total frame count."""

    @property
    def total_pairs(self) -> int:
        """Number of FramePairs (total_frames - 1)."""
        return max(0, self.total_frames - 1)

    @abstractmethod
    def __iter__(self) -> Iterator[FramePair]:
        """
        Iterate over frame pairs.

        Yields:
            FramePair with read-only FrameViews.
            WARNING: Views are invalidated on next iteration.
        """

    @abstractmethod
    def close(self) -> None:
        """Release resources (reader, buffers, threads)."""

    def __enter__(self) -> FrameSource:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
