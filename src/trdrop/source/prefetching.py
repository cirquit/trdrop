"""Prefetching frame source with background I/O."""

from __future__ import annotations

from queue import Queue
from threading import Thread
from typing import Iterator

import numpy as np

from trdrop.interfaces.source import FrameSource
from trdrop.interfaces.video import VideoReader
from trdrop.types.frames import FramePair, FrameView


class _FrameData:
    """Internal: frame data passed through queue."""

    __slots__ = ("buffer", "index", "pts")

    def __init__(self, buffer: np.ndarray, index: int, pts: int) -> None:
        self.buffer = buffer
        self.index = index
        self.pts = pts


class PrefetchingFrameSource(FrameSource):
    """
    Frame source with background prefetching.

    A background thread reads frames into a queue while
    the main thread processes. Hides I/O latency.
    """

    def __init__(self, reader: VideoReader, prefetch: int = 2) -> None:
        self._reader = reader
        self._prefetch = prefetch
        self._queue: Queue[_FrameData | None] = Queue(maxsize=prefetch)
        self._thread: Thread | None = None
        self._stop_requested = False

    @property
    def fps(self) -> float:
        return self._reader.fps

    @property
    def total_frames(self) -> int:
        return self._reader.total_frames

    def _prefetch_loop(self) -> None:
        """Background: read frames into queue."""
        self._reader.seek(0)
        frame_idx = 0

        while not self._stop_requested:
            buffer = np.empty(self._reader.frame_shape, dtype=np.uint8)

            if not self._reader.read(buffer):
                break

            self._queue.put(_FrameData(buffer, frame_idx, pts=frame_idx))
            frame_idx += 1

        self._queue.put(None)

    def __iter__(self) -> Iterator[FramePair]:
        self._stop_requested = False
        self._thread = Thread(target=self._prefetch_loop, daemon=True)
        self._thread.start()

        prev_data = self._queue.get()
        if prev_data is None:
            return

        while True:
            curr_data = self._queue.get()
            if curr_data is None:
                break

            yield FramePair(
                prev=FrameView(
                    _data=prev_data.buffer,
                    index=prev_data.index,
                    pts=prev_data.pts,
                ),
                curr=FrameView(
                    _data=curr_data.buffer,
                    index=curr_data.index,
                    pts=curr_data.pts,
                ),
            )

            prev_data = curr_data

    def close(self) -> None:
        self._stop_requested = True
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        self._reader.close()
