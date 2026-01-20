"""Default color palettes for video overlays."""

from __future__ import annotations

from PyQt6.QtGui import QColor

# Default colors for up to 8 videos - visually distinct and colorblind-friendly
DEFAULT_VIDEO_COLORS = [
    QColor(100, 200, 100),   # Green - Video 1
    QColor(100, 150, 255),   # Blue - Video 2
    QColor(255, 150, 100),   # Orange - Video 3
    QColor(200, 100, 200),   # Purple - Video 4
    QColor(255, 200, 100),   # Yellow - Video 5
    QColor(100, 200, 200),   # Cyan - Video 6
    QColor(255, 100, 150),   # Pink - Video 7
    QColor(180, 180, 180),   # Gray - Video 8
]


def get_video_color(video_index: int) -> QColor:
    """Get the default color for a video index.

    Args:
        video_index: Zero-based video index.

    Returns:
        QColor for the video. Cycles through palette if index exceeds palette size.
    """
    return DEFAULT_VIDEO_COLORS[video_index % len(DEFAULT_VIDEO_COLORS)]
