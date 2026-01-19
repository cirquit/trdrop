"""Mock frame source for testing."""

from __future__ import annotations

from typing import Iterator

import numpy as np

from trdrop.interfaces.source import FrameSource
from trdrop.types.frames import FramePair, FrameView


class MockFrameSource(FrameSource):
    """
    Mock source for testing.

    Generates frames without actual video file.
    """

    def __init__(
        self,
        total_frames: int,
        fps: float = 60.0,
        frame_shape: tuple[int, int, int] = (480, 640, 3),
    ) -> None:
        self._total_frames = total_frames
        self._fps = fps
        self._frame_shape = frame_shape

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def total_frames(self) -> int:
        return self._total_frames

    def __iter__(self) -> Iterator[FramePair]:
        prev_buf = np.zeros(self._frame_shape, dtype=np.uint8)

        for i in range(1, self._total_frames):
            curr_buf = np.full(self._frame_shape, i % 256, dtype=np.uint8)

            yield FramePair(
                prev=FrameView(_data=prev_buf, index=i - 1, pts=i - 1),
                curr=FrameView(_data=curr_buf, index=i, pts=i),
            )

            prev_buf = curr_buf

    def close(self) -> None:
        pass
