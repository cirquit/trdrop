"""Text overlay elements."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter


class TextAlign(Enum):
    """Text alignment options."""

    LEFT = auto()
    RIGHT = auto()
    CENTER = auto()


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
        align: TextAlign = TextAlign.LEFT,
    ) -> None:
        self._style = style
        self._prefix = prefix
        self._align = align

    def draw(
        self,
        painter: QPainter,
        position: QPoint,
        fps: float,
        bounds_width: int | None = None,
    ) -> None:
        """Draw FPS text at position.

        Args:
            painter: QPainter to draw with
            position: Anchor position for text (meaning depends on alignment)
            fps: Current FPS value to display
            bounds_width: Width of bounding area (for right/center alignment)
        """
        text = f"{self._prefix} {fps:.1f}"

        painter.setFont(self._style.font)

        # Calculate text width for alignment
        metrics = QFontMetrics(self._style.font)
        text_width = metrics.horizontalAdvance(text)

        # Calculate actual x position based on alignment
        x = position.x()
        if self._align == TextAlign.RIGHT and bounds_width is not None:
            x = position.x() + bounds_width - text_width
        elif self._align == TextAlign.CENTER and bounds_width is not None:
            x = position.x() + (bounds_width - text_width) // 2

        draw_pos = QPoint(x, position.y())

        # Draw shadow
        shadow_pos = QPoint(
            draw_pos.x() + self._style.shadow_offset,
            draw_pos.y() + self._style.shadow_offset,
        )
        painter.setPen(self._style.shadow_color)
        painter.drawText(shadow_pos, text)

        # Draw main text
        painter.setPen(self._style.color)
        painter.drawText(draw_pos, text)


class FrametimeText:
    """Stateless frametime text renderer.

    Configured at construction with style and label prefix.
    Draw receives the current frametime value in milliseconds.
    """

    def __init__(
        self,
        style: TextStyle,
        prefix: str = "ms:",
        align: TextAlign = TextAlign.LEFT,
        decimal_places: int = 2,
    ) -> None:
        self._style = style
        self._prefix = prefix
        self._align = align
        self._decimal_places = decimal_places

    def draw(
        self,
        painter: QPainter,
        position: QPoint,
        frametime_ms: float,
        bounds_width: int | None = None,
    ) -> None:
        """Draw frametime text at position.

        Args:
            painter: QPainter to draw with
            position: Anchor position for text (meaning depends on alignment)
            frametime_ms: Current frametime value in milliseconds
            bounds_width: Width of bounding area (for right/center alignment)
        """
        text = f"{self._prefix} {frametime_ms:.{self._decimal_places}f}"

        painter.setFont(self._style.font)

        # Calculate text width for alignment
        metrics = QFontMetrics(self._style.font)
        text_width = metrics.horizontalAdvance(text)

        # Calculate actual x position based on alignment
        x = position.x()
        if self._align == TextAlign.RIGHT and bounds_width is not None:
            x = position.x() + bounds_width - text_width
        elif self._align == TextAlign.CENTER and bounds_width is not None:
            x = position.x() + (bounds_width - text_width) // 2

        draw_pos = QPoint(x, position.y())

        # Draw shadow
        shadow_pos = QPoint(
            draw_pos.x() + self._style.shadow_offset,
            draw_pos.y() + self._style.shadow_offset,
        )
        painter.setPen(self._style.shadow_color)
        painter.drawText(shadow_pos, text)

        # Draw main text
        painter.setPen(self._style.color)
        painter.drawText(draw_pos, text)
