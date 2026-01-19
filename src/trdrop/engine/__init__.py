"""TRDrop analysis engine."""

from __future__ import annotations

from trdrop.engine.streaming import StreamingEngine
from trdrop.engine.trdrop import TrdropEngine, VideoResult

__all__ = [
    "StreamingEngine",
    "TrdropEngine",
    "VideoResult",
]
