"""Video viewport widget."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class VideoViewport(QWidget):
    """Widget for displaying a video frame with overlay."""

    def __init__(self, video_index: int) -> None:
        super().__init__()

        self._video_index = video_index
        self._frame_data: bytes | None = None
        self._fps: float = 0.0
        self._frametime: float = 0.0

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the viewport UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        # Video display area (placeholder for now)
        self._display = QLabel()
        self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._display.setStyleSheet("background-color: #1a1a1a; color: #666;")
        self._display.setText(f"Video {self._video_index + 1}")
        self._display.setMinimumSize(320, 180)
        layout.addWidget(self._display, stretch=1)

        # Info label
        self._info = QLabel()
        self._info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._info.setStyleSheet("color: #888; font-size: 11px;")
        self._update_info()
        layout.addWidget(self._info)

    def _update_info(self) -> None:
        """Update the info label."""
        if self._fps > 0:
            self._info.setText(f"FPS: {self._fps:.1f} | Frametime: {self._frametime:.1f}ms")
        else:
            self._info.setText("Waiting for analysis...")

    def set_frame(self, frame_data: bytes, width: int, height: int) -> None:
        """Set the current frame to display."""
        # TODO: Convert frame data to QPixmap and display
        self._frame_data = frame_data
        self.update()

    def set_stats(self, fps: float, frametime: float) -> None:
        """Update the stats display."""
        self._fps = fps
        self._frametime = frametime
        self._update_info()

    def paintEvent(self, a0: object) -> None:
        """Paint the viewport."""
        # For now, just let the layout handle it
        super().paintEvent(a0)  # type: ignore[arg-type]
