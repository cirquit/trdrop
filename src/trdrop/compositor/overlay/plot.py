"""Plot overlay elements."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from PyQt6.QtCore import QPoint, QPointF, QRect, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen

from trdrop.profiling import get_profiler
from trdrop.utils.ringbuffer import RingBuffer


def _format_fps_label(value: float) -> str:
    """Format FPS value for display, using K suffix for thousands."""
    if value >= 1000:
        k_value = value / 1000
        if k_value == int(k_value):
            return f"{int(k_value)}K"
        return f"{k_value:.1f}K"
    return f"{value:.0f}"


def _moving_average(values: list[float], window: int) -> list[float]:
    """Compute simple moving average for smoothing."""
    if window <= 1 or len(values) < window:
        return values

    result: list[float] = []
    window_sum = sum(values[:window])
    result.append(window_sum / window)

    for i in range(window, len(values)):
        window_sum += values[i] - values[i - window]
        result.append(window_sum / window)

    return result


def _nice_max_fps(max_value: float, segments: int = 4) -> float:
    """Round up to a nice value divisible by segments.

    Returns values like 60, 120, 240, 300, 400, 500, 1000, 2000, etc.
    """
    if max_value <= 0:
        return float(segments)

    # Nice increments: prefer multiples of segments that look clean
    nice_bases = [10, 12, 15, 20, 25, 30, 40, 50, 60, 100, 120, 150, 200, 250, 300, 400, 500]

    for base in nice_bases:
        candidate = base * segments
        if candidate >= max_value:
            return float(candidate)

    # For very large values, round up to nearest (1000 * segments)
    k_units = int(max_value / (1000 * segments)) + 1
    return float(k_units * 1000 * segments)


@dataclass(frozen=True, slots=True)
class PlotStyle:
    """Visual styling for a plot."""

    line_color: QColor
    background_color: QColor
    axis_color: QColor
    grid_color: QColor
    text_color: QColor
    shadow_color: QColor
    font: QFont
    title_font: QFont | None = None  # Larger font for title, defaults to font
    line_width: int = 3
    shadow_offset: int = 2
    show_grid: bool = True
    show_labels: bool = True
    grid_segments: int = 4


class Plot(ABC):
    """Base class for stateless plot renderers."""

    def __init__(self, style: PlotStyle, title: str = "") -> None:
        self._style = style
        self._title = title

    @abstractmethod
    def draw(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
    ) -> None:
        """Draw plot into bounds using history data."""

    def _draw_background(self, painter: QPainter, bounds: QRect) -> None:
        """Draw semi-transparent background."""
        painter.fillRect(bounds, self._style.background_color)

    def _draw_axes(self, painter: QPainter, bounds: QRect) -> None:
        """Draw X and Y axes with shadow."""
        pen = QPen(self._style.axis_color)
        pen.setWidth(2)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)

        # Y axis (left edge)
        painter.drawLine(bounds.left(), bounds.top(), bounds.left(), bounds.bottom())
        # X axis (bottom edge)
        painter.drawLine(bounds.left(), bounds.bottom(), bounds.right(), bounds.bottom())

    def _draw_grid(self, painter: QPainter, bounds: QRect) -> None:
        """Draw horizontal grid lines."""
        if not self._style.show_grid:
            return

        pen = QPen(self._style.grid_color)
        pen.setWidth(1)
        painter.setPen(pen)

        segments = self._style.grid_segments
        segment_height = bounds.height() / segments

        for i in range(segments):
            y = int(bounds.top() + i * segment_height)
            painter.drawLine(bounds.left(), y, bounds.right(), y)

    def _draw_text_with_shadow(
        self,
        painter: QPainter,
        pos: QPoint,
        text: str,
    ) -> None:
        """Draw text with shadow for contrast."""
        offset = self._style.shadow_offset

        # Shadow
        painter.setPen(self._style.shadow_color)
        painter.drawText(pos.x() + offset, pos.y() + offset, text)

        # Main text
        painter.setPen(self._style.text_color)
        painter.drawText(pos.x(), pos.y(), text)

    def _draw_labels(
        self,
        painter: QPainter,
        bounds: QRect,
        y_min: float,
        y_max: float,
    ) -> None:
        """Draw Y-axis labels on the RIGHT side of the plot."""
        if not self._style.show_labels:
            return

        painter.setFont(self._style.font)

        segments = self._style.grid_segments
        segment_height = bounds.height() / segments
        value_step = (y_max - y_min) / segments

        for i in range(segments + 1):
            y = int(bounds.top() + i * segment_height)
            value = y_max - i * value_step
            label = _format_fps_label(value)

            # Draw to the RIGHT of plot area
            text_x = bounds.right() + 5
            text_y = y + 4
            self._draw_text_with_shadow(painter, QPoint(text_x, text_y), label)

    def _draw_title(self, painter: QPainter, bounds: QRect) -> None:
        """Draw title above the plot on the right side."""
        if not self._title:
            return

        title_font = self._style.title_font or self._style.font
        painter.setFont(title_font)

        # Position: above plot, right-aligned
        x = bounds.right() - bounds.width() // 10
        y = bounds.top() - bounds.height() // 10

        self._draw_text_with_shadow(painter, QPoint(x, y), self._title)


class FrameratePlot(Plot):
    """Plot for framerate history (0 to max_fps).

    Set auto_scale=True to dynamically adjust max_fps based on data.
    When auto_scale is enabled, max_fps serves as the minimum scale.
    """

    def __init__(
        self,
        style: PlotStyle,
        max_fps: float = 60.0,
        show_center_line: bool = True,
        title: str = "FRAMERATE",
        auto_scale: bool = False,
        show_smoothed: bool = True,
        time_anchor: float = 1.0,
    ) -> None:
        """Initialize framerate plot.

        Args:
            style: Visual styling for the plot.
            max_fps: Maximum FPS for Y-axis (or minimum when auto_scale=True).
            show_center_line: Draw horizontal line at half max FPS.
            title: Title text above the plot.
            auto_scale: Dynamically adjust Y-axis based on data.
            show_smoothed: Show fading smoothed trail behind exact line.
            time_anchor: Where current time appears horizontally.
                0.0 = left edge, 0.5 = center, 1.0 = right edge (default).
        """
        super().__init__(style, title)
        self._max_fps = max_fps
        self._min_scale = max_fps  # Minimum scale when auto_scale is on
        self._show_center_line = show_center_line
        self._auto_scale = auto_scale
        self._show_smoothed = show_smoothed
        self._time_anchor = max(0.0, min(1.0, time_anchor))

    def _get_effective_max(self, history: RingBuffer) -> float:
        """Get the effective max FPS for scaling.

        Uses only the most recent 10% of the buffer for scale calculation,
        allowing the scale to adapt quickly when FPS drops.
        """
        if not self._auto_scale or len(history) == 0:
            return self._max_fps

        # Use recent values only (last 10% of buffer) for faster adaptation
        values = list(history)
        recent_count = max(len(values) // 10, 10)  # At least 10 samples
        recent_values = values[-recent_count:]

        max_in_data = max(recent_values)

        # Use at least the minimum scale
        target = max(max_in_data * 1.1, self._min_scale)  # 10% headroom

        # Round to nice value
        return _nice_max_fps(target, self._style.grid_segments)

    def draw(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
    ) -> None:
        """Draw framerate plot."""
        profiler = get_profiler()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        effective_max = self._get_effective_max(history)

        t0 = time.perf_counter()
        self._draw_background(painter, bounds)
        profiler.add_timing("overlay_plot_background", (time.perf_counter() - t0) * 1000)

        t0 = time.perf_counter()
        self._draw_grid(painter, bounds)
        if self._show_center_line:
            self._draw_center_line(painter, bounds)
        profiler.add_timing("overlay_plot_grid", (time.perf_counter() - t0) * 1000)

        # Draw line before axes so axes appear on top
        t0 = time.perf_counter()
        self._draw_line(painter, bounds, history, effective_max)
        profiler.add_timing("overlay_plot_line", (time.perf_counter() - t0) * 1000)

        t0 = time.perf_counter()
        self._draw_axes(painter, bounds)
        profiler.add_timing("overlay_plot_axes", (time.perf_counter() - t0) * 1000)

        t0 = time.perf_counter()
        self._draw_labels(painter, bounds, 0.0, effective_max)
        profiler.add_timing("overlay_plot_labels", (time.perf_counter() - t0) * 1000)

        t0 = time.perf_counter()
        self._draw_title(painter, bounds)
        profiler.add_timing("overlay_plot_title", (time.perf_counter() - t0) * 1000)

    def _draw_center_line(self, painter: QPainter, bounds: QRect) -> None:
        """Draw horizontal center line at half max FPS."""
        pen = QPen(self._style.grid_color)
        pen.setWidth(1)
        painter.setPen(pen)

        center_y = bounds.top() + bounds.height() // 2
        painter.drawLine(bounds.left(), center_y, bounds.right(), center_y)

    def _draw_line(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
        max_fps: float | None = None,
    ) -> None:
        """Draw the framerate line(s) with shadow for contrast.

        Draws a fading smoothed trail behind the exact data line.
        The smoothed line fades out towards the current time (anchor position),
        leaving the exact line clearly visible at the front.
        """
        if len(history) < 2:
            return

        if max_fps is None:
            max_fps = self._max_fps

        values = list(history)
        n = len(values)

        # Calculate positioning based on time_anchor
        # time_anchor=1.0: current time at right edge (default)
        # time_anchor=0.5: current time at center
        x_step = bounds.width() / max(history.size - 1, 1)
        y_scale = bounds.height() / max_fps

        # Position so newest data point is at anchor position
        anchor_x = bounds.left() + bounds.width() * self._time_anchor
        newest_idx = n - 1
        x_base = anchor_x - newest_idx * x_step

        # Draw fading smoothed trail first (behind exact line)
        if self._show_smoothed and n >= 5:
            profiler = get_profiler()
            t0 = time.perf_counter()
            self._draw_fading_trail(painter, bounds, values, x_step, x_base, y_scale, n)
            profiler.add_timing("overlay_plot_trail", (time.perf_counter() - t0) * 1000)

        # Build and draw exact data path (on top, fully visible)
        exact_path = QPainterPath()
        for i in range(n):
            x = x_base + i * x_step
            y = bounds.bottom() - values[i] * y_scale
            y = max(float(bounds.top()), min(float(bounds.bottom()), y))
            if i == 0:
                exact_path.moveTo(QPointF(x, y))
            else:
                exact_path.lineTo(QPointF(x, y))

        # Draw exact line with full visibility
        shadow_pen = QPen(self._style.shadow_color)
        shadow_pen.setWidthF(self._style.line_width + 2.0)
        shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(shadow_pen)
        painter.drawPath(exact_path)

        line_pen = QPen(self._style.line_color)
        line_pen.setWidthF(float(self._style.line_width))
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.drawPath(exact_path)

    def _draw_fading_trail(
        self,
        painter: QPainter,
        bounds: QRect,
        values: list[float],
        x_step: float,
        x_base: float,
        y_scale: float,
        n: int,
    ) -> None:
        """Draw a smoothed trail that fades towards the current time (anchor)."""
        # Apply smoothing
        window = max(3, n // 15)  # ~7% of data points
        smoothed = _moving_average(values, window)

        if len(smoothed) < 2:
            return

        # Draw trail in segments with decreasing opacity towards current time
        num_segments = 8
        segment_len = max(1, len(smoothed) // num_segments)

        for seg in range(num_segments):
            start_idx = seg * segment_len
            end_idx = min(start_idx + segment_len + 1, len(smoothed))

            if end_idx - start_idx < 2:
                continue

            # Opacity fades from old (high) to new/current (low)
            # segment 0 = oldest = brightest, segment N = newest = dimmest
            opacity = int(160 * (1.0 - seg / num_segments))
            if opacity < 15:
                continue

            seg_path = QPainterPath()
            for i in range(start_idx, end_idx):
                orig_idx = i + window // 2
                if orig_idx >= n:
                    break
                x = x_base + orig_idx * x_step
                y = bounds.bottom() - smoothed[i] * y_scale
                y = max(float(bounds.top()), min(float(bounds.bottom()), y))
                if i == start_idx:
                    seg_path.moveTo(QPointF(x, y))
                else:
                    seg_path.lineTo(QPointF(x, y))

            # Draw segment with faded color
            trail_color = QColor(self._style.line_color)
            trail_color.setAlpha(opacity)
            trail_shadow = QColor(self._style.shadow_color)
            trail_shadow.setAlpha(opacity // 3)

            shadow_pen = QPen(trail_shadow)
            shadow_pen.setWidthF(self._style.line_width + 3.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(shadow_pen)
            painter.drawPath(seg_path)

            trail_pen = QPen(trail_color)
            trail_pen.setWidthF(self._style.line_width + 1.0)
            trail_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            trail_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(trail_pen)
            painter.drawPath(seg_path)


class FrametimePlot(Plot):
    """Plot for frametime history (0 to max_ms)."""

    def __init__(
        self,
        style: PlotStyle,
        max_ms: float = 50.0,
        title: str = "FRAMETIME (ms)",
    ) -> None:
        super().__init__(style, title)
        self._max_ms = max_ms

    def draw(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
    ) -> None:
        """Draw frametime plot."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._draw_background(painter, bounds)
        self._draw_grid(painter, bounds)

        # Draw line before axes so axes appear on top
        self._draw_line(painter, bounds, history)

        self._draw_axes(painter, bounds)
        self._draw_labels(painter, bounds, 0.0, self._max_ms)
        self._draw_title(painter, bounds)

    def _draw_line(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
    ) -> None:
        """Draw the frametime line with shadow.

        Uses QPainterPath with floating-point coordinates for smooth antialiasing.
        """
        if len(history) < 2:
            return

        values = list(history)
        n = len(values)

        x_step = bounds.width() / max(history.size - 1, 1)
        y_scale = bounds.height() / self._max_ms
        x_offset = (history.size - n) * x_step

        # Build path with floating-point precision for smooth antialiasing
        path = QPainterPath()
        first_point = True

        for i in range(n):
            x = bounds.left() + x_offset + i * x_step
            y = bounds.bottom() - values[i] * y_scale
            y = max(float(bounds.top()), min(float(bounds.bottom()), y))

            if first_point:
                path.moveTo(QPointF(x, y))
                first_point = False
            else:
                path.lineTo(QPointF(x, y))

        # Shadow line
        shadow_pen = QPen(self._style.shadow_color)
        shadow_pen.setWidthF(self._style.line_width + 2.0)
        shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(shadow_pen)
        painter.drawPath(path)

        # Main line
        line_pen = QPen(self._style.line_color)
        line_pen.setWidthF(float(self._style.line_width))
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.drawPath(path)
