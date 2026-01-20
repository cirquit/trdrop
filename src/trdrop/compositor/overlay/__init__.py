"""Overlay rendering elements for compositor."""

from __future__ import annotations

from trdrop.compositor.overlay.colors import DEFAULT_VIDEO_COLORS, get_video_color
from trdrop.compositor.overlay.plot import (
    FrameratePlot,
    FrametimePlot,
    Plot,
    PlotSeries,
    PlotStyle,
)
from trdrop.compositor.overlay.text import FPSText, FrametimeText, TextAlign

__all__ = [
    "DEFAULT_VIDEO_COLORS",
    "FPSText",
    "FrameratePlot",
    "FrametimePlot",
    "FrametimeText",
    "Plot",
    "PlotSeries",
    "PlotStyle",
    "TextAlign",
    "get_video_color",
]
