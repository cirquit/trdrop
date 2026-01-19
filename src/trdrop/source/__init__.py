"""FrameSource implementations."""

from __future__ import annotations

from trdrop.source.mock import MockFrameSource
from trdrop.source.prefetching import PrefetchingFrameSource
from trdrop.source.sequential import SequentialFrameSource

__all__ = [
    "MockFrameSource",
    "PrefetchingFrameSource",
    "SequentialFrameSource",
]
