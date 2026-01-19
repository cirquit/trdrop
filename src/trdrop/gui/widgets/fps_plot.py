"""FPS plot widget."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget


class FPSPlotWidget(QWidget):
    """Widget for displaying FPS over time."""

    # Colors for up to 4 videos
    COLORS = [
        QColor(66, 133, 244),  # Blue
        QColor(234, 67, 53),   # Red
        QColor(52, 168, 83),   # Green
        QColor(251, 188, 4),   # Yellow
    ]

    def __init__(self) -> None:
        super().__init__()

        # TODO: Adapt to use VideoResultBuffer instead of Session
        self._fps_window = 60
        self._visible_frames = 300

        self.setMinimumHeight(100)

    def set_fps_window(self, window: int) -> None:
        """Set the window size for FPS calculation."""
        self._fps_window = window
        self.update()

    def paintEvent(self, a0: object) -> None:
        """Paint the FPS plot."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # TODO: Implement FPS plot with new pipeline types
        # Draw placeholder text
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            "Run analysis to see FPS plot",
        )

        painter.end()
