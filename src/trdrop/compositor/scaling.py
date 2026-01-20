"""Scaling modes for video composition.

Defines how source video frames are placed into destination slots
when dimensions don't match exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class ScaleMode(Enum):
    """How to handle size mismatch between source video and destination slot.

    Used by the compositor to determine placement strategy when
    source dimensions differ from the allocated slot dimensions.
    """

    CROP = auto()
    """Show center portion of source, crop excess. Fastest option."""

    FIT = auto()
    """Scale source to fit within slot, preserve aspect ratio, letterbox with black."""

    STRETCH = auto()
    """Scale source to exactly fill slot, ignoring aspect ratio."""


@dataclass(frozen=True, slots=True)
class ScaleModeInfo:
    """Metadata about a scale mode for GUI display and documentation.

    Attributes:
        mode: The scale mode this info describes.
        label: Short display label for GUI (e.g., dropdown menu).
        description: Longer description for tooltips.
        performance_impact: Performance classification.
        performance_note: Optional warning text about performance.
    """

    mode: ScaleMode
    label: str
    description: str
    performance_impact: PerformanceImpact
    performance_note: str | None = None


class PerformanceImpact(Enum):
    """Performance classification for GUI display."""

    FAST = auto()
    """No scaling, direct memory copy."""

    MODERATE = auto()
    """Some computation required but optimized."""

    SLOW = auto()
    """Significant computation, may impact real-time performance."""


# Registry of scale mode metadata
_SCALE_MODE_INFO: dict[ScaleMode, ScaleModeInfo] = {
    ScaleMode.CROP: ScaleModeInfo(
        mode=ScaleMode.CROP,
        label="Crop",
        description="Show center portion of video, crop edges if larger than slot. "
        "No scaling applied - fastest option for same-resolution videos.",
        performance_impact=PerformanceImpact.FAST,
    ),
    ScaleMode.FIT: ScaleModeInfo(
        mode=ScaleMode.FIT,
        label="Fit (Letterbox)",
        description="Scale video to fit within slot while preserving aspect ratio. "
        "Black bars added if aspect ratios differ.",
        performance_impact=PerformanceImpact.SLOW,
        performance_note="Requires frame scaling. Consider using Crop mode for "
        "same-resolution videos to improve performance.",
    ),
    ScaleMode.STRETCH: ScaleModeInfo(
        mode=ScaleMode.STRETCH,
        label="Stretch",
        description="Scale video to exactly fill slot, ignoring aspect ratio. "
        "May distort the image.",
        performance_impact=PerformanceImpact.SLOW,
        performance_note="Requires frame scaling. Consider using Crop mode for "
        "same-resolution videos to improve performance.",
    ),
}


def get_scale_mode_info(mode: ScaleMode) -> ScaleModeInfo:
    """Get metadata for a scale mode.

    Args:
        mode: The scale mode to get info for.

    Returns:
        ScaleModeInfo with label, description, and performance notes.
    """
    return _SCALE_MODE_INFO[mode]


def get_all_scale_modes() -> list[ScaleModeInfo]:
    """Get metadata for all scale modes, ordered for GUI display.

    Returns:
        List of ScaleModeInfo, with recommended (fast) modes first.
    """
    # Order: fast modes first
    order = [ScaleMode.CROP, ScaleMode.FIT, ScaleMode.STRETCH]
    return [_SCALE_MODE_INFO[mode] for mode in order]


def has_performance_warning(mode: ScaleMode) -> bool:
    """Check if a scale mode has a performance warning.

    Args:
        mode: The scale mode to check.

    Returns:
        True if the mode may impact performance.
    """
    info = _SCALE_MODE_INFO[mode]
    return info.performance_note is not None
