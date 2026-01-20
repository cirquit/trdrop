"""Benchmark different line drawing strategies.

Run with: uv run pytest tests/benchmarks/test_line_strategies.py -v -s
"""

from __future__ import annotations

import sys
import time

import numpy as np
import pytest
from PyQt6.QtCore import QPointF, QRect, Qt
from PyQt6.QtGui import (
    QColor,
    QGuiApplication,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)


@pytest.fixture(scope="module")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app


def generate_history(size: int, seed: int = 42) -> list[float]:
    """Generate random FPS history."""
    rng = np.random.default_rng(seed)
    return [30.0 + rng.random() * 30.0 for _ in range(size)]


class TestLineStrategies:
    """Benchmark different line drawing approaches."""

    def test_line_strategies(self, qapp):
        """Compare different line drawing methods."""
        width, height = 1920, 1080
        qimage = QImage(width, height, QImage.Format.Format_RGB888)

        bounds = QRect(100, 750, 800, 200)
        history_size = 60
        values = generate_history(history_size)

        # Pre-calculate points
        max_fps = 60.0
        x_step = bounds.width() / max(history_size - 1, 1)
        y_scale = bounds.height() / max_fps
        time_anchor = 0.5

        anchor_x = bounds.left() + bounds.width() * time_anchor
        newest_idx = len(values) - 1
        x_base = anchor_x - newest_idx * x_step

        points = []
        for i, v in enumerate(values):
            x = x_base + i * x_step
            y = bounds.bottom() - v * y_scale
            y = max(float(bounds.top()), min(float(bounds.bottom()), y))
            points.append(QPointF(x, y))

        line_color = QColor(255, 100, 200)
        shadow_color = QColor(0, 0, 0)
        line_width = 2

        n_iterations = 100
        warmup = 10

        strategies = {}

        # Strategy 1: QPainterPath (current implementation)
        def draw_path_double(painter):
            """Current: build path, draw shadow, draw line."""
            path = QPainterPath()
            for i, pt in enumerate(points):
                if i == 0:
                    path.moveTo(pt)
                else:
                    path.lineTo(pt)

            # Shadow
            shadow_pen = QPen(shadow_color)
            shadow_pen.setWidthF(line_width + 2.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(shadow_pen)
            painter.drawPath(path)

            # Main
            line_pen = QPen(line_color)
            line_pen.setWidthF(float(line_width))
            line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(line_pen)
            painter.drawPath(path)

        # Strategy 2: QPolygonF + drawPolyline
        polygon = QPolygonF(points)

        def draw_polyline_double(painter):
            """Use drawPolyline instead of drawPath."""
            # Shadow
            shadow_pen = QPen(shadow_color)
            shadow_pen.setWidthF(line_width + 2.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(shadow_pen)
            painter.drawPolyline(polygon)

            # Main
            line_pen = QPen(line_color)
            line_pen.setWidthF(float(line_width))
            line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(line_pen)
            painter.drawPolyline(polygon)

        # Strategy 3: Pre-built QPainterPath (cached)
        cached_path = QPainterPath()
        for i, pt in enumerate(points):
            if i == 0:
                cached_path.moveTo(pt)
            else:
                cached_path.lineTo(pt)

        def draw_path_cached(painter):
            """Use pre-built path (simulating caching)."""
            # Shadow
            shadow_pen = QPen(shadow_color)
            shadow_pen.setWidthF(line_width + 2.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(shadow_pen)
            painter.drawPath(cached_path)

            # Main
            line_pen = QPen(line_color)
            line_pen.setWidthF(float(line_width))
            line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(line_pen)
            painter.drawPath(cached_path)

        # Strategy 4: No shadow
        def draw_polyline_no_shadow(painter):
            """Single polyline, no shadow."""
            line_pen = QPen(line_color)
            line_pen.setWidthF(float(line_width))
            line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(line_pen)
            painter.drawPolyline(polygon)

        # Strategy 5: Downsampled (every 2nd point)
        downsampled_points = points[::2]
        downsampled_polygon = QPolygonF(downsampled_points)

        def draw_downsampled(painter):
            """Downsampled polyline (half points)."""
            # Shadow
            shadow_pen = QPen(shadow_color)
            shadow_pen.setWidthF(line_width + 2.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(shadow_pen)
            painter.drawPolyline(downsampled_polygon)

            # Main
            line_pen = QPen(line_color)
            line_pen.setWidthF(float(line_width))
            line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(line_pen)
            painter.drawPolyline(downsampled_polygon)

        # Strategy 6: No antialiasing
        def draw_polyline_no_aa(painter):
            """Polyline without antialiasing."""
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

            # Shadow
            shadow_pen = QPen(shadow_color)
            shadow_pen.setWidthF(line_width + 2.0)
            painter.setPen(shadow_pen)
            painter.drawPolyline(polygon)

            # Main
            line_pen = QPen(line_color)
            line_pen.setWidthF(float(line_width))
            painter.setPen(line_pen)
            painter.drawPolyline(polygon)

            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Strategy 7: drawLines (individual segments)
        def draw_lines(painter):
            """Draw individual line segments."""
            # Shadow
            shadow_pen = QPen(shadow_color)
            shadow_pen.setWidthF(line_width + 2.0)
            shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(shadow_pen)
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

            # Main
            line_pen = QPen(line_color)
            line_pen.setWidthF(float(line_width))
            line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(line_pen)
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

        strategies = {
            "path_double (current)": draw_path_double,
            "polyline_double": draw_polyline_double,
            "path_cached": draw_path_cached,
            "polyline_no_shadow": draw_polyline_no_shadow,
            "downsampled_2x": draw_downsampled,
            "polyline_no_aa": draw_polyline_no_aa,
            "drawLines": draw_lines,
        }

        results = {}

        for name, draw_fn in strategies.items():
            qimage.fill(0)

            # Warmup
            for _ in range(warmup):
                painter = QPainter(qimage)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                draw_fn(painter)
                painter.end()

            # Benchmark
            t0 = time.perf_counter()
            for _ in range(n_iterations):
                painter = QPainter(qimage)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                draw_fn(painter)
                painter.end()
            results[name] = (time.perf_counter() - t0) / n_iterations * 1000

        # Print results
        print("\n")
        print("=" * 70)
        print("LINE DRAWING STRATEGY COMPARISON")
        print("=" * 70)
        print(f"Points: {len(points)}, Iterations: {n_iterations}")
        print()

        baseline = results["path_double (current)"]

        print(f"{'Strategy':<25} {'Time (ms)':<12} {'Speedup':<12}")
        print("-" * 55)

        sorted_results = sorted(results.items(), key=lambda x: x[1])
        for name, ms in sorted_results:
            speedup = baseline / ms if ms > 0 else 0
            marker = " <-- current" if name == "path_double (current)" else ""
            print(f"{name:<25} {ms:<12.4f} {speedup:<12.2f}x{marker}")

        print("=" * 70)

    def test_point_count_vs_strategy(self, qapp):
        """Compare strategies at different point counts."""
        width, height = 1920, 1080
        qimage = QImage(width, height, QImage.Format.Format_RGB888)

        bounds = QRect(100, 750, 800, 200)
        line_color = QColor(255, 100, 200)
        shadow_color = QColor(0, 0, 0)
        line_width = 2

        n_iterations = 50
        warmup = 5

        print("\n")
        print("=" * 80)
        print("POINT COUNT VS STRATEGY PERFORMANCE")
        print("=" * 80)
        print()

        print(f"{'Points':<10} {'Path (ms)':<12} {'Polyline (ms)':<14} "
              f"{'Cached (ms)':<12} {'Speedup':<10}")
        print("-" * 65)

        for n_points in [30, 60, 120, 240]:
            values = generate_history(n_points)
            max_fps = 60.0
            x_step = bounds.width() / max(n_points - 1, 1)
            y_scale = bounds.height() / max_fps

            points = []
            for i, v in enumerate(values):
                x = bounds.left() + i * x_step
                y = bounds.bottom() - v * y_scale
                y = max(float(bounds.top()), min(float(bounds.bottom()), y))
                points.append(QPointF(x, y))

            polygon = QPolygonF(points)
            cached_path = QPainterPath()
            for i, pt in enumerate(points):
                if i == 0:
                    cached_path.moveTo(pt)
                else:
                    cached_path.lineTo(pt)

            def draw_path():
                painter = QPainter(qimage)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                for i, pt in enumerate(points):
                    if i == 0:
                        path.moveTo(pt)
                    else:
                        path.lineTo(pt)

                shadow_pen = QPen(shadow_color)
                shadow_pen.setWidthF(line_width + 2.0)
                shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(shadow_pen)
                painter.drawPath(path)

                line_pen = QPen(line_color)
                line_pen.setWidthF(float(line_width))
                line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(line_pen)
                painter.drawPath(path)
                painter.end()

            def draw_polyline():
                painter = QPainter(qimage)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                shadow_pen = QPen(shadow_color)
                shadow_pen.setWidthF(line_width + 2.0)
                shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(shadow_pen)
                painter.drawPolyline(polygon)

                line_pen = QPen(line_color)
                line_pen.setWidthF(float(line_width))
                line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(line_pen)
                painter.drawPolyline(polygon)
                painter.end()

            def draw_cached():
                painter = QPainter(qimage)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                shadow_pen = QPen(shadow_color)
                shadow_pen.setWidthF(line_width + 2.0)
                shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                shadow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(shadow_pen)
                painter.drawPath(cached_path)

                line_pen = QPen(line_color)
                line_pen.setWidthF(float(line_width))
                line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(line_pen)
                painter.drawPath(cached_path)
                painter.end()

            # Warmup and benchmark each
            for _ in range(warmup):
                draw_path()
                draw_polyline()
                draw_cached()

            t0 = time.perf_counter()
            for _ in range(n_iterations):
                draw_path()
            path_ms = (time.perf_counter() - t0) / n_iterations * 1000

            t0 = time.perf_counter()
            for _ in range(n_iterations):
                draw_polyline()
            polyline_ms = (time.perf_counter() - t0) / n_iterations * 1000

            t0 = time.perf_counter()
            for _ in range(n_iterations):
                draw_cached()
            cached_ms = (time.perf_counter() - t0) / n_iterations * 1000

            speedup = path_ms / polyline_ms if polyline_ms > 0 else 0
            print(f"{n_points:<10} {path_ms:<12.3f} {polyline_ms:<14.3f} "
                  f"{cached_ms:<12.3f} {speedup:.2f}x")

        print("=" * 80)
