"""TRDrop analysis engine."""

from __future__ import annotations

from trdrop.engine.buffer import FrameSnapshot, ProcessingBuffer
from trdrop.engine.interactive import InteractiveEngine, LoadResult
from trdrop.engine.protocol import (
    ConfigurationError,
    EngineProgress,
    EngineState,
    InteractiveEngineProtocol,
    InvalidStateError,
    OnError,
    OnFrameProcessed,
    OnProgress,
    OnStateChange,
    SeekResult,
)
from trdrop.engine.streaming import StreamingEngine
from trdrop.engine.trdrop import TrdropEngine, VideoResult

__all__ = [
    # Buffer types
    "FrameSnapshot",
    "ProcessingBuffer",
    # Protocol and types
    "ConfigurationError",
    "EngineProgress",
    "EngineState",
    "InteractiveEngineProtocol",
    "InvalidStateError",
    "LoadResult",
    "OnError",
    "OnFrameProcessed",
    "OnProgress",
    "OnStateChange",
    "SeekResult",
    # Implementations
    "InteractiveEngine",
    "StreamingEngine",
    "TrdropEngine",
    "VideoResult",
]
