"""Sequential frame source - no prefetching."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Iterator

import numpy as np

from trdrop.interfaces.source import FrameSource
from trdrop.interfaces.video import VideoReader
from trdrop.types.frames import FramePair, FrameView, ReleaseCallback

if TYPE_CHECKING:
    from trdrop.source.sequential import SequentialFrameSource as SelfType


class _SequentialReleaseCallback(ReleaseCallback):
    """Release callback for SequentialFrameSource."""

    def __init__(self, source: SelfType) -> None:
        self._source = source

    def __call__(self) -> None:
        self._source._pending_release = False


class SequentialFrameSource(FrameSource):
    """
    Simple sequential frame source with double-buffering.

    No prefetching - reads are blocking. Uses two buffers that alternate
    between holding prev and curr frames.

    Callers MUST call release() on each FramePair before requesting the next.
    Failure to release will emit a warning (future: may block or error).
    """

    def __init__(self, reader: VideoReader) -> None:
        self._reader = reader
        self._buffer_a = np.empty(reader.frame_shape, dtype=np.uint8)
        self._buffer_b = np.empty(reader.frame_shape, dtype=np.uint8)
        self._pending_release = False
        self._release_callback = _SequentialReleaseCallback(self)

    @property
    def fps(self) -> float:
        return self._reader.fps

    @property
    def total_frames(self) -> int:
        return self._reader.total_frames

    def __iter__(self) -> Iterator[FramePair]:
        self._reader.seek(0)
        self._pending_release = False
        prev_buf, curr_buf = self._buffer_a, self._buffer_b

        if not self._reader.read(prev_buf):
            return

        frame_idx = 1
        prev_pts = 0

        while self._reader.read(curr_buf):
            if self._pending_release:
                warnings.warn(
                    "FramePair not released before next iteration. "
                    "Call pair.release() when done processing.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                self._pending_release = False

            curr_pts = frame_idx
            self._pending_release = True

            yield FramePair(
                prev=FrameView(_data=prev_buf, index=frame_idx - 1, pts=prev_pts),
                curr=FrameView(_data=curr_buf, index=frame_idx, pts=curr_pts),
                _on_release=self._release_callback,
            )

            prev_buf, curr_buf = curr_buf, prev_buf
            prev_pts = curr_pts
            frame_idx += 1

    def close(self) -> None:
        self._reader.close()
