"""Plot overlay elements."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from PyQt6.QtCore import QPoint, QPointF, QRect, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap

from trdrop.profiling import get_profiler
from trdrop.utils.ringbuffer import RingBuffer


def _font_px(font: QFont) -> int:
    """Get font size in pixels, whether set via pixelSize or pointSize."""
    ps = font.pixelSize()
    return ps if ps > 0 else max(1, font.pointSize())


def _format_fps_label(value: float) -> str:
    """Format FPS value for display, using K suffix for thousands."""
    if value >= 1000:
        k_value = value / 1000
        if k_value == int(k_value):
            return f"{int(k_value)}K"
        return f"{k_value:.1f}K"
    return f"{value:.0f}"


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


def _nice_max_ms(max_value: float, segments: int = 4) -> float:
    """Round up to a nice ms value divisible by segments.

    Returns values like 16.67, 33.33, 50, 100, 200, etc.
    """
    if max_value <= 0:
        return float(segments)

    # Nice bases for frametime (prefer common refresh rate frametimes)
    nice_values = [16.67, 20, 25, 33.33, 40, 50, 66.67, 80, 100, 125, 150, 200, 250, 500, 1000]

    for v in nice_values:
        if v >= max_value:
            return v

    # For very large values, round up to nearest 100ms
    return float(((int(max_value) // 100) + 1) * 100)


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
    show_shadow: bool = True  # Draw shadow behind line/text for contrast


@dataclass(slots=True)
class PlotSeries:
    """A single data series for multi-series plots."""

    history: RingBuffer
    color: QColor
    label: str = ""


class Plot(ABC):
    """Base class for plot renderers with static element caching.

    Static elements (background, grid, axes, labels) are rendered once to a
    cached pixmap and reused each frame. Only the dynamic line is redrawn.
    """

    def __init__(self, style: PlotStyle, title: str = "") -> None:
        self._style = style
        self._title = title
        # Static element cache
        self._static_cache: QPixmap | None = None
        self._cached_bounds: QRect | None = None
        self._cached_scale: float = 0.0  # y_max used when cache was built

    @abstractmethod
    def draw(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
    ) -> None:
        """Draw plot into bounds using history data."""

    def _needs_cache_rebuild(self, bounds: QRect, y_max: float) -> bool:
        """Check if static cache needs to be rebuilt."""
        if self._static_cache is None:
            return True
        if self._cached_bounds != bounds:
            return True
        if self._cached_scale != y_max:
            return True
        return False

    def _draw_static_cache(self, painter: QPainter, bounds: QRect) -> None:
        """Blit the static cache to the painter."""
        if self._static_cache is not None:
            painter.drawPixmap(bounds.topLeft(), self._static_cache)

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
        """Draw text with black outline for contrast (like DF-style overlays)."""
        painter.save()

        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        # Build text path for outline
        path = QPainterPath()
        path.addText(QPointF(pos.x(), pos.y()), font, text)

        # Draw black outline
        outline_width = max(2.0, _font_px(font) / 8.0)
        outline_pen = QPen(self._style.shadow_color)
        outline_pen.setWidthF(outline_width)
        outline_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(outline_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Fill with text color
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._style.text_color)
        painter.drawPath(path)

        painter.restore()

    def _draw_labels(
        self,
        painter: QPainter,
        bounds: QRect,
        y_min: float,
        y_max: float,
        time_anchor: float = 1.0,
    ) -> None:
        """Draw Y-axis labels at the time anchor position."""
        if not self._style.show_labels:
            return

        painter.setFont(self._style.font)

        segments = self._style.grid_segments
        segment_height = bounds.height() / segments
        value_step = (y_max - y_min) / segments

        # Position labels at the anchor point (where "now" is displayed)
        # Use (width - 1) for Qt rect semantics
        plot_width = bounds.width() - 1
        anchor_x = bounds.left() + int(plot_width * time_anchor)

        for i in range(segments + 1):
            y = int(bounds.top() + i * segment_height)
            value = y_max - i * value_step
            label = _format_fps_label(value)

            # Draw to the right of the anchor position
            font_size = _font_px(self._style.font)
            pad_x = max(8, font_size // 2)
            pad_y = font_size // 3
            text_x = anchor_x + pad_x
            text_y = y + pad_y
            self._draw_text_with_shadow(painter, QPoint(text_x, text_y), label)

    def _draw_title(
        self,
        painter: QPainter,
        bounds: QRect,
        time_anchor: float = 1.0,
    ) -> None:
        """Draw title above the plot, right-aligned at the time anchor position.

        Args:
            painter: QPainter to draw with
            bounds: Plot bounds
            time_anchor: X position as fraction (0.0=left, 1.0=right)
        """
        if not self._title:
            return

        title_font = self._style.title_font or self._style.font
        painter.setFont(title_font)

        # Calculate text width for right-alignment
        from PyQt6.QtGui import QFontMetrics
        metrics = QFontMetrics(title_font)
        text_width = metrics.horizontalAdvance(self._title)

        # Position: above plot, right-aligned at time_anchor position
        # Use (width - 1) for Qt rect semantics
        plot_width = bounds.width() - 1
        anchor_x = bounds.left() + int(plot_width * time_anchor)
        x = anchor_x - text_width  # Right-align to anchor
        font_size = _font_px(title_font)
        y = bounds.top() - max(8, font_size // 2)  # Gap scales with font

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
        time_anchor: float = 1.0,
        show_title: bool = True,
        show_time_indicator: bool = False,
        show_start_marker: bool = False,
    ) -> None:
        """Initialize framerate plot.

        Args:
            style: Visual styling for the plot.
            max_fps: Maximum FPS for Y-axis (or minimum when auto_scale=True).
            show_center_line: Draw horizontal line at half max FPS.
            title: Title text above the plot.
            auto_scale: Dynamically adjust Y-axis based on data.
            time_anchor: Where current time appears horizontally.
                0.0 = left edge, 0.5 = center, 1.0 = right edge (default).
            show_title: Whether to display the title above the plot.
            show_time_indicator: Draw downward arrow at current time position.
            show_start_marker: Draw small circle at line start.
        """
        super().__init__(style, title)
        self._max_fps = max_fps
        self._min_scale = max_fps  # Minimum scale when auto_scale is on
        self._show_center_line = show_center_line
        self._auto_scale = auto_scale
        self._time_anchor = max(0.0, min(1.0, time_anchor))
        self._show_title = show_title
        self._show_time_indicator = show_time_indicator
        self._show_start_marker = show_start_marker

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
        target = max(max_in_data * 1.25, self._min_scale)  # 25% headroom

        # Round to nice value
        return _nice_max_fps(target, self._style.grid_segments)

    def draw(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
        *,
        override_show_title: bool | None = None,
    ) -> None:
        """Draw framerate plot.

        Args:
            painter: QPainter to draw with
            bounds: Rectangle to draw into
            history: FPS history data
            override_show_title: If set, overrides the instance's show_title setting
        """
        profiler = get_profiler()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        effective_max = self._get_effective_max(history)
        show_title = override_show_title if override_show_title is not None else self._show_title

        # Build or use static element cache
        t0 = time.perf_counter()
        if self._needs_cache_rebuild(bounds, effective_max):
            self._build_framerate_cache(bounds, effective_max, show_title)
        self._draw_static_cache(painter, bounds)
        profiler.add_timing("overlay_plot_background", (time.perf_counter() - t0) * 1000)

        # Draw dynamic line (clipped to bounds)
        t0 = time.perf_counter()
        painter.save()
        painter.setClipRect(bounds)
        line_points = self._draw_line(painter, bounds, history, effective_max)
        painter.restore()
        profiler.add_timing("overlay_plot_line", (time.perf_counter() - t0) * 1000)

        # Draw markers after line (outside clip region so they can extend beyond)
        t0 = time.perf_counter()
        if line_points and self._show_start_marker:
            self._draw_start_marker(painter, line_points[0])
        if line_points and self._show_time_indicator:
            self._draw_time_indicator(painter, bounds, line_points[-1])
        profiler.add_timing("overlay_plot_markers", (time.perf_counter() - t0) * 1000)

    def _build_framerate_cache(
        self, bounds: QRect, effective_max: float, show_title: bool
    ) -> None:
        """Build static cache for framerate plot."""
        # Create pixmap with transparent background
        self._static_cache = QPixmap(bounds.size())
        self._static_cache.fill(QColor(0, 0, 0, 0))

        cache_painter = QPainter(self._static_cache)
        cache_painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw to local coordinates (0,0 based)
        local_bounds = QRect(0, 0, bounds.width(), bounds.height())

        self._draw_background(cache_painter, local_bounds)
        self._draw_grid(cache_painter, local_bounds)
        if self._show_center_line:
            self._draw_center_line(cache_painter, local_bounds)
        self._draw_anchor_line(cache_painter, local_bounds)
        self._draw_axes(cache_painter, local_bounds)
        self._draw_labels(cache_painter, local_bounds, 0.0, effective_max, self._time_anchor)
        if show_title:
            self._draw_title(cache_painter, local_bounds, self._time_anchor)

        cache_painter.end()

        self._cached_bounds = QRect(bounds)
        self._cached_scale = effective_max

    def _draw_center_line(self, painter: QPainter, bounds: QRect) -> None:
        """Draw horizontal center line at half max FPS."""
        pen = QPen(self._style.grid_color)
        pen.setWidth(1)
        painter.setPen(pen)

        center_y = bounds.top() + bounds.height() // 2
        painter.drawLine(bounds.left(), center_y, bounds.right(), center_y)

    def _draw_anchor_line(self, painter: QPainter, bounds: QRect) -> None:
        """Draw vertical line at the time anchor position (where 'now' is)."""
        if self._time_anchor >= 0.99:
            # Skip if anchor is at far right (would overlap with axis)
            return

        pen = QPen(self._style.line_color)
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        # Use (width - 1) for Qt rect semantics
        plot_width = bounds.width() - 1
        anchor_x = bounds.left() + int(plot_width * self._time_anchor)
        painter.drawLine(anchor_x, bounds.top(), anchor_x, bounds.bottom())

    def _draw_line(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
        max_fps: float | None = None,
    ) -> list[QPointF]:
        """Draw the framerate line with optional shadow for contrast.

        Returns list of points (first=oldest, last=newest) for marker drawing.

        Performance note: Shadow is drawn without antialiasing for speed.
        The main line is drawn with AA for quality. This hybrid approach
        provides ~2x speedup vs full AA on both passes.
        """
        if len(history) < 2:
            return []

        if max_fps is None:
            max_fps = self._max_fps

        values = list(history)
        n = len(values)

        # Calculate positioning based on time_anchor
        # time_anchor=1.0: current time at right edge (default)
        # time_anchor=0.5: current time at center
        # Note: Use (width - 1) to account for Qt rect semantics where
        # right() = left() + width() - 1
        plot_width = bounds.width() - 1
        x_step = plot_width / max(history.size - 1, 1)
        y_scale = bounds.height() / max_fps

        # Position so newest data point is at anchor position
        anchor_x = bounds.left() + plot_width * self._time_anchor
        newest_idx = n - 1
        x_base = anchor_x - newest_idx * x_step

        # Build path and collect points
        path = QPainterPath()
        points: list[QPointF] = []
        for i in range(n):
            x = x_base + i * x_step
            y = bounds.bottom() - values[i] * y_scale
            y = max(float(bounds.top()), min(float(bounds.bottom()), y))
            pt = QPointF(x, y)
            points.append(pt)
            if i == 0:
                path.moveTo(pt)
            else:
                path.lineTo(pt)

        # Draw shadow (without AA for performance - shadow is just for contrast)
        if self._style.show_shadow:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            shadow_pen = QPen(self._style.shadow_color)
            shadow_pen.setWidthF(self._style.line_width + 2.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            shadow_pen.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
            painter.setPen(shadow_pen)
            painter.drawPath(path)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Draw main line (with AA for quality)
        line_pen = QPen(self._style.line_color)
        line_pen.setWidthF(float(self._style.line_width))
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.drawPath(path)

        return points

    def _draw_start_marker(self, painter: QPainter, point: QPointF) -> None:
        """Draw a small circle at the start of the line."""
        radius = self._style.line_width + 2
        # Shadow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._style.shadow_color)
        painter.drawEllipse(point, radius + 1, radius + 1)
        # Main circle
        painter.setBrush(self._style.line_color)
        painter.drawEllipse(point, radius, radius)
        # Reset brush to prevent filling subsequent paths
        painter.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_time_indicator(
        self, painter: QPainter, bounds: QRect, point: QPointF
    ) -> None:
        """Draw a downward arrow at current time position."""
        # Larger triangle pointing down, above the plot
        arrow_size = 12
        tip_y = bounds.top() - 3
        base_y = tip_y - arrow_size

        path = QPainterPath()
        path.moveTo(point.x(), tip_y)  # Tip
        path.lineTo(point.x() - arrow_size // 2, base_y)  # Left
        path.lineTo(point.x() + arrow_size // 2, base_y)  # Right
        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._style.line_color)
        painter.drawPath(path)
        # Reset brush to prevent filling subsequent paths
        painter.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_line_with_color(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
        color: QColor,
        max_fps: float,
    ) -> list[QPointF]:
        """Draw a line with a specific color (for combined mode).

        Similar to _draw_line but uses the provided color instead of style.line_color.
        """
        if len(history) < 2:
            return []

        values = list(history)
        n = len(values)

        plot_width = bounds.width() - 1
        x_step = plot_width / max(history.size - 1, 1)
        y_scale = bounds.height() / max_fps

        anchor_x = bounds.left() + plot_width * self._time_anchor
        newest_idx = n - 1
        x_base = anchor_x - newest_idx * x_step

        path = QPainterPath()
        points: list[QPointF] = []
        for i in range(n):
            x = x_base + i * x_step
            y = bounds.bottom() - values[i] * y_scale
            y = max(float(bounds.top()), min(float(bounds.bottom()), y))
            pt = QPointF(x, y)
            points.append(pt)
            if i == 0:
                path.moveTo(pt)
            else:
                path.lineTo(pt)

        # Draw shadow
        if self._style.show_shadow:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            shadow_pen = QPen(self._style.shadow_color)
            shadow_pen.setWidthF(self._style.line_width + 2.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            shadow_pen.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
            painter.setPen(shadow_pen)
            painter.drawPath(path)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Draw main line with specified color
        line_pen = QPen(color)
        line_pen.setWidthF(float(self._style.line_width))
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.drawPath(path)

        return points

    def draw_combined(
        self,
        painter: QPainter,
        bounds: QRect,
        series_list: list[PlotSeries],
        *,
        override_show_title: bool | None = None,
    ) -> None:
        """Draw multiple data series on a single plot (combined mode).

        Args:
            painter: QPainter to draw with
            bounds: Rectangle to draw into
            series_list: List of PlotSeries (history + color for each video)
            override_show_title: If set, overrides the instance's show_title setting
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Compute effective max across all series
        all_values: list[float] = []
        for s in series_list:
            if len(s.history) > 0:
                all_values.extend(list(s.history))

        if self._auto_scale and all_values:
            # Use recent values for scale
            recent_count = max(len(all_values) // 10, 10)
            recent_values = all_values[-recent_count:]
            max_in_data = max(recent_values)
            target = max(max_in_data * 1.25, self._min_scale)
            effective_max = _nice_max_fps(target, self._style.grid_segments)
        else:
            effective_max = self._max_fps

        self._draw_background(painter, bounds)
        self._draw_grid(painter, bounds)
        if self._show_center_line:
            self._draw_center_line(painter, bounds)
        self._draw_anchor_line(painter, bounds)

        # Draw each series with its color (clipped to bounds)
        painter.save()
        painter.setClipRect(bounds)
        for s in series_list:
            self._draw_line_with_color(painter, bounds, s.history, s.color, effective_max)
        painter.restore()

        self._draw_axes(painter, bounds)
        self._draw_labels(painter, bounds, 0.0, effective_max, self._time_anchor)

        show_title = override_show_title if override_show_title is not None else self._show_title
        if show_title:
            self._draw_title(painter, bounds, self._time_anchor)


class FrametimePlot(Plot):
    """Plot for frametime history (0 to max_ms).

    Shows frametime in milliseconds with optional auto-scaling and
    current value display next to the title.
    """

    def __init__(
        self,
        style: PlotStyle,
        max_ms: float = 50.0,
        title: str = "FRAMETIME",
        auto_scale: bool = True,
        time_anchor: float = 1.0,
        show_title: bool = True,
        show_current_value: bool = True,
        show_time_indicator: bool = False,
        show_start_marker: bool = False,
    ) -> None:
        """Initialize frametime plot.

        Args:
            style: Visual styling for the plot.
            max_ms: Maximum frametime for Y-axis (or minimum when auto_scale=True).
            title: Title text above the plot.
            auto_scale: Dynamically adjust Y-axis based on data.
            time_anchor: Where current time appears horizontally.
                0.0 = left edge, 0.5 = center, 1.0 = right edge (default).
            show_title: Whether to display the title above the plot.
            show_current_value: Show current frametime value next to title.
            show_time_indicator: Draw downward arrow at current time position.
            show_start_marker: Draw small circle at line start.
        """
        super().__init__(style, title)
        self._max_ms = max_ms
        self._min_scale = max_ms
        self._auto_scale = auto_scale
        self._time_anchor = max(0.0, min(1.0, time_anchor))
        self._show_title = show_title
        self._show_current_value = show_current_value
        self._show_time_indicator = show_time_indicator
        self._show_start_marker = show_start_marker

    def _get_effective_max(self, history: RingBuffer) -> float:
        """Get the effective max frametime for scaling."""
        if not self._auto_scale or len(history) == 0:
            return self._max_ms

        values = list(history)
        recent_count = max(len(values) // 10, 10)
        recent_values = values[-recent_count:]

        max_in_data = max(recent_values) if recent_values else 0

        target = max(max_in_data * 1.25, self._min_scale)

        # Round to nice values for frametime (multiples of 10, 16.67, 33.33, etc.)
        nice_values = [10, 16.67, 20, 33.33, 40, 50, 66.67, 100, 200, 500, 1000]
        for nv in nice_values:
            if nv >= target:
                return nv
        return target

    def draw(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
        *,
        current_value: float | None = None,
        override_show_title: bool | None = None,
    ) -> None:
        """Draw frametime plot.

        Args:
            painter: QPainter to draw with.
            bounds: Rectangle to draw into.
            history: Frametime history data (in ms).
            current_value: Current frametime to display (optional, for title).
            override_show_title: If set, overrides the instance's show_title setting.
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        effective_max = self._get_effective_max(history)
        show_title = override_show_title if override_show_title is not None else self._show_title

        # Build or use static element cache (excludes title since it has dynamic value)
        if self._needs_cache_rebuild(bounds, effective_max):
            self._build_frametime_cache(bounds, effective_max)
        self._draw_static_cache(painter, bounds)

        # Draw dynamic line (clipped to bounds)
        painter.save()
        painter.setClipRect(bounds)
        line_points = self._draw_line(painter, bounds, history, effective_max)
        painter.restore()

        # Draw markers after line (outside clip region)
        if line_points and self._show_start_marker:
            self._draw_start_marker(painter, line_points[0])
        if line_points and self._show_time_indicator:
            self._draw_time_indicator(painter, bounds, line_points[-1])

        # Title drawn each frame since it has dynamic current_value
        if show_title:
            self._draw_title_with_value(painter, bounds, current_value)

    def _build_frametime_cache(self, bounds: QRect, effective_max: float) -> None:
        """Build static cache for frametime plot (excludes dynamic title)."""
        self._static_cache = QPixmap(bounds.size())
        self._static_cache.fill(QColor(0, 0, 0, 0))

        cache_painter = QPainter(self._static_cache)
        cache_painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        local_bounds = QRect(0, 0, bounds.width(), bounds.height())

        self._draw_background(cache_painter, local_bounds)
        self._draw_grid(cache_painter, local_bounds)
        self._draw_axes(cache_painter, local_bounds)
        self._draw_labels_fractional(cache_painter, local_bounds, 0.0, effective_max)

        cache_painter.end()

        self._cached_bounds = QRect(bounds)
        self._cached_scale = effective_max

    def _draw_labels_fractional(
        self,
        painter: QPainter,
        bounds: QRect,
        y_min: float,
        y_max: float,
    ) -> None:
        """Draw Y-axis labels with fractional values on the RIGHT side."""
        if not self._style.show_labels:
            return

        painter.setFont(self._style.font)

        segments = self._style.grid_segments
        segment_height = bounds.height() / segments
        value_step = (y_max - y_min) / segments

        for i in range(segments + 1):
            y = int(bounds.top() + i * segment_height)
            value = y_max - i * value_step

            # Format with appropriate precision
            if value >= 100:
                label = f"{value:.0f}"
            elif value >= 10:
                label = f"{value:.1f}"
            else:
                label = f"{value:.2f}"

            # Draw to the RIGHT of plot area (same as FrameratePlot)
            font_size = _font_px(self._style.font)
            pad_x = max(8, font_size // 2)
            pad_y = font_size // 3
            text_x = bounds.right() + pad_x
            text_y = y + pad_y
            self._draw_text_with_shadow(painter, QPoint(text_x, text_y), label)

    def _draw_title_with_value(
        self,
        painter: QPainter,
        bounds: QRect,
        current_value: float | None,
    ) -> None:
        """Draw title with optional current value."""
        if not self._title:
            return

        title_font = self._style.title_font or self._style.font
        painter.setFont(title_font)

        # Build title text
        if self._show_current_value and current_value is not None:
            if current_value >= 100:
                title_text = f"{self._title}: {current_value:.1f}ms"
            else:
                title_text = f"{self._title}: {current_value:.2f}ms"
        else:
            title_text = self._title

        # Position at left (time_anchor for consistency)
        from PyQt6.QtGui import QFontMetrics
        metrics = QFontMetrics(title_font)
        text_width = metrics.horizontalAdvance(title_text)

        # Use (width - 1) for Qt rect semantics
        plot_width = bounds.width() - 1
        anchor_x = bounds.left() + int(plot_width * self._time_anchor)
        x = anchor_x - text_width
        y = bounds.top() - 8

        self._draw_text_with_shadow(painter, QPoint(x, y), title_text)

    def _draw_line(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
        max_ms: float | None = None,
    ) -> list[QPointF]:
        """Draw the frametime line with optional shadow.

        Returns list of points (first=oldest, last=newest) for marker drawing.

        Performance note: Shadow is drawn without antialiasing for speed.
        The main line is drawn with AA for quality.
        """
        if len(history) < 2:
            return []

        if max_ms is None:
            max_ms = self._max_ms

        values = list(history)
        n = len(values)

        # Use (width - 1) for Qt rect semantics
        plot_width = bounds.width() - 1
        x_step = plot_width / max(history.size - 1, 1)
        y_scale = bounds.height() / max_ms

        # Position so newest data point is at anchor position
        anchor_x = bounds.left() + plot_width * self._time_anchor
        newest_idx = n - 1
        x_base = anchor_x - newest_idx * x_step

        path = QPainterPath()
        points: list[QPointF] = []
        for i in range(n):
            x = x_base + i * x_step
            y = bounds.bottom() - values[i] * y_scale
            y = max(float(bounds.top()), min(float(bounds.bottom()), y))
            pt = QPointF(x, y)
            points.append(pt)

            if i == 0:
                path.moveTo(pt)
            else:
                path.lineTo(pt)

        # Shadow line (without AA for performance)
        if self._style.show_shadow:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            shadow_pen = QPen(self._style.shadow_color)
            shadow_pen.setWidthF(self._style.line_width + 2.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            shadow_pen.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
            painter.setPen(shadow_pen)
            painter.drawPath(path)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Main line (with AA for quality)
        line_pen = QPen(self._style.line_color)
        line_pen.setWidthF(float(self._style.line_width))
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.drawPath(path)

        return points

    def _draw_start_marker(self, painter: QPainter, point: QPointF) -> None:
        """Draw a small circle at the start of the line."""
        radius = self._style.line_width + 2
        # Shadow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._style.shadow_color)
        painter.drawEllipse(point, radius + 1, radius + 1)
        # Main circle
        painter.setBrush(self._style.line_color)
        painter.drawEllipse(point, radius, radius)
        # Reset brush to prevent filling subsequent paths
        painter.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_time_indicator(
        self, painter: QPainter, bounds: QRect, point: QPointF
    ) -> None:
        """Draw a downward arrow at current time position."""
        # Larger triangle pointing down, above the plot
        arrow_size = 12
        tip_y = bounds.top() - 3
        base_y = tip_y - arrow_size

        path = QPainterPath()
        path.moveTo(point.x(), tip_y)  # Tip
        path.lineTo(point.x() - arrow_size // 2, base_y)  # Left
        path.lineTo(point.x() + arrow_size // 2, base_y)  # Right
        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._style.line_color)
        painter.drawPath(path)
        # Reset brush to prevent filling subsequent paths
        painter.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_line_with_color(
        self,
        painter: QPainter,
        bounds: QRect,
        history: RingBuffer,
        color: QColor,
        max_ms: float,
    ) -> list[QPointF]:
        """Draw a line with a specific color (for combined mode)."""
        if len(history) < 2:
            return []

        values = list(history)
        n = len(values)

        plot_width = bounds.width() - 1
        x_step = plot_width / max(history.size - 1, 1)
        y_scale = bounds.height() / max_ms

        anchor_x = bounds.left() + plot_width * self._time_anchor
        newest_idx = n - 1
        x_base = anchor_x - newest_idx * x_step

        path = QPainterPath()
        points: list[QPointF] = []
        for i in range(n):
            x = x_base + i * x_step
            y = bounds.bottom() - values[i] * y_scale
            y = max(float(bounds.top()), min(float(bounds.bottom()), y))
            pt = QPointF(x, y)
            points.append(pt)
            if i == 0:
                path.moveTo(pt)
            else:
                path.lineTo(pt)

        # Shadow
        if self._style.show_shadow:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            shadow_pen = QPen(self._style.shadow_color)
            shadow_pen.setWidthF(self._style.line_width + 2.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            shadow_pen.setJoinStyle(Qt.PenJoinStyle.BevelJoin)
            painter.setPen(shadow_pen)
            painter.drawPath(path)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Main line with specified color
        line_pen = QPen(color)
        line_pen.setWidthF(float(self._style.line_width))
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.drawPath(path)

        return points

    def draw_combined(
        self,
        painter: QPainter,
        bounds: QRect,
        series_list: list[PlotSeries],
        *,
        current_values: list[float] | None = None,
        override_show_title: bool | None = None,
    ) -> None:
        """Draw multiple data series on a single plot (combined mode).

        Args:
            painter: QPainter to draw with
            bounds: Rectangle to draw into
            series_list: List of PlotSeries (history + color for each video)
            current_values: Current frametime values for display (optional)
            override_show_title: If set, overrides the instance's show_title setting
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Compute effective max across all series
        all_values: list[float] = []
        for s in series_list:
            if len(s.history) > 0:
                all_values.extend(list(s.history))

        if self._auto_scale and all_values:
            max_in_data = max(all_values)
            target = max(max_in_data * 1.25, self._min_scale)
            effective_max = _nice_max_ms(target, self._style.grid_segments)
        else:
            effective_max = self._max_ms

        self._draw_background(painter, bounds)
        self._draw_grid(painter, bounds)

        # Draw each series with its color (clipped to bounds)
        painter.save()
        painter.setClipRect(bounds)
        for s in series_list:
            self._draw_line_with_color(painter, bounds, s.history, s.color, effective_max)
        painter.restore()

        self._draw_axes(painter, bounds)
        self._draw_labels_fractional(painter, bounds, 0.0, effective_max)

        show_title = override_show_title if override_show_title is not None else self._show_title
        if show_title:
            # For combined mode, show first current value if available
            current_value = current_values[0] if current_values else None
            self._draw_title_with_value(painter, bounds, current_value)
