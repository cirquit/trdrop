"""Compositor module for frame composition and metric aggregation."""

from __future__ import annotations

from trdrop.compositor.base import Compositor
from trdrop.compositor.scaling import (
    PerformanceImpact,
    ScaleMode,
    ScaleModeInfo,
    get_all_scale_modes,
    get_scale_mode_info,
    has_performance_warning,
)
from trdrop.compositor.simple import SimpleCompositor
from trdrop.compositor.types import AggregatedMetrics, CompositorOutput, VideoMetrics

__all__ = [
    "AggregatedMetrics",
    "Compositor",
    "CompositorOutput",
    "PerformanceImpact",
    "ScaleMode",
    "ScaleModeInfo",
    "SimpleCompositor",
    "VideoMetrics",
    "get_all_scale_modes",
    "get_scale_mode_info",
    "has_performance_warning",
]
