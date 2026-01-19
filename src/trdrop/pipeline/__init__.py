"""Pipeline module for video analysis processing."""

from __future__ import annotations

from trdrop.pipeline.analyzers import DuplicateAnalyzer, TearAnalyzer
from trdrop.pipeline.exporters import Exporter
from trdrop.pipeline.pipeline import ProcessingPipeline
from trdrop.pipeline.renderers import Renderer
from trdrop.pipeline.storage import FrameResultSlot, VideoResultBuffer
from trdrop.pipeline.types import (
    CompositeFrameState,
    DuplicateResult,
    TearResult,
    VideoFrameState,
)

__all__ = [
    # Types
    "CompositeFrameState",
    "DuplicateResult",
    "TearResult",
    "VideoFrameState",
    # Storage
    "FrameResultSlot",
    "VideoResultBuffer",
    # Analyzers
    "DuplicateAnalyzer",
    "TearAnalyzer",
    # Protocols
    "Exporter",
    "Renderer",
    # Pipeline
    "ProcessingPipeline",
]
