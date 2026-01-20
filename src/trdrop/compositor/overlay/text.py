"""Text overlay elements."""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QColor, QFont, QPainter


@dataclass(frozen=True, slots=True)
class TextStyle:
    """Visual styling for text overlays."""

    color: QColor
    shadow_color: QColor
    font: QFont
    shadow_offset: int = 2


class FPSText:
    """Stateless FPS text renderer.

    Configured at construction with style and label prefix.
    Draw receives the current FPS value.
    """

    def __init__(
        self,
        style: TextStyle,
        prefix: str = "FPS:",
    ) -> None:
        self._style = style
        self._prefix = prefix

    def draw(
        self,
        painter: QPainter,
        position: QPoint,
        fps: float,
    ) -> None:
        """Draw FPS text at position.

        Args:
            painter: QPainter to draw with
            position: Top-left position for text
            fps: Current FPS value to display
        """
        text = f"{self._prefix} {fps:.1f}"

        painter.setFont(self._style.font)

        # Draw shadow
        shadow_pos = QPoint(
            position.x() + self._style.shadow_offset,
            position.y() + self._style.shadow_offset,
        )
        painter.setPen(self._style.shadow_color)
        painter.drawText(shadow_pos, text)

        # Draw main text
        painter.setPen(self._style.color)
        painter.drawText(position, text)
