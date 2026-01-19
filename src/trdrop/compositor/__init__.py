"""Compositor module for frame composition and metric aggregation."""

from __future__ import annotations

from trdrop.compositor.base import Compositor
from trdrop.compositor.simple import SimpleCompositor
from trdrop.compositor.types import AggregatedMetrics, CompositorOutput, VideoMetrics

__all__ = [
    "AggregatedMetrics",
    "Compositor",
    "CompositorOutput",
    "SimpleCompositor",
    "VideoMetrics",
]
