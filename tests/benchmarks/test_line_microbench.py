"""Micro-benchmark to isolate line drawing bottlenecks.

Run with: uv run pytest tests/benchmarks/test_line_microbench.py -v -s
"""

from __future__ import annotations

import sys
import time

import pytest
from PyQt6.QtCore import QPointF, QRect, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPainterPath, QPen, QPolygonF

from trdrop.utils.ringbuffer import RingBuffer


@pytest.fixture(scope="module")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app  # type: ignore[return-value]


class TestLineMicrobench:
    """Micro-benchmarks to isolate line drawing bottlenecks."""

    def test_breakdown(self, qapp):
        """Break down where time is spent in line drawing."""
        # Setup
        width, height = 800, 200
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(QColor(0, 0, 0, 0))

        # Create history with 60 points
        history = RingBuffer(60)
        for i in range(60):
            history.push(30.0 + 15.0 * (i % 10) / 10)  # Varying FPS

        _bounds = QRect(0, 0, width, height)  # noqa: F841
        iterations = 100
        warmup = 10

        # Benchmark components
        results = {}

        # 1. list(history) - RingBuffer to list conversion
        for _ in range(warmup):
            _ = list(history)
        t0 = time.perf_counter()
        for _ in range(iterations):
            values = list(history)
        results["list(history)"] = (time.perf_counter() - t0) / iterations * 1000

        values = list(history)
        n = len(values)

        # 2. Path construction (moveTo/lineTo loop)
        x_step = width / (n - 1)
        y_scale = height / 60.0

        for _ in range(warmup):
            path = QPainterPath()
            for i in range(n):
                x = i * x_step
                y = height - values[i] * y_scale
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)

        t0 = time.perf_counter()
        for _ in range(iterations):
            path = QPainterPath()
            for i in range(n):
                x = i * x_step
                y = height - values[i] * y_scale
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
        results["path construction"] = (time.perf_counter() - t0) / iterations * 1000

        # Build path once for render tests
        path = QPainterPath()
        for i in range(n):
            x = i * x_step
            y = height - values[i] * y_scale
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        # 3. QPen creation
        for _ in range(warmup):
            pen = QPen(QColor(255, 100, 200))
            pen.setWidthF(3.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        t0 = time.perf_counter()
        for _ in range(iterations):
            pen = QPen(QColor(255, 100, 200))
            pen.setWidthF(3.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        results["QPen creation"] = (time.perf_counter() - t0) / iterations * 1000

        # Create pen once for render tests
        pen = QPen(QColor(255, 100, 200))
        pen.setWidthF(3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        # 4. drawPath WITHOUT antialiasing
        for _ in range(warmup):
            painter = QPainter(image)
            painter.setPen(pen)
            painter.drawPath(path)
            painter.end()

        t0 = time.perf_counter()
        for _ in range(iterations):
            painter = QPainter(image)
            painter.setPen(pen)
            painter.drawPath(path)
            painter.end()
        results["drawPath (no AA)"] = (time.perf_counter() - t0) / iterations * 1000

        # 5. drawPath WITH antialiasing
        for _ in range(warmup):
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(pen)
            painter.drawPath(path)
            painter.end()

        t0 = time.perf_counter()
        for _ in range(iterations):
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(pen)
            painter.drawPath(path)
            painter.end()
        results["drawPath (with AA)"] = (time.perf_counter() - t0) / iterations * 1000

        # 6. drawPolyline alternative
        points_list = [QPointF(i * x_step, height - values[i] * y_scale) for i in range(n)]
        polygon = QPolygonF(points_list)

        for _ in range(warmup):
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(pen)
            painter.drawPolyline(polygon)
            painter.end()

        t0 = time.perf_counter()
        for _ in range(iterations):
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(pen)
            painter.drawPolyline(polygon)
            painter.end()
        results["drawPolyline (with AA)"] = (time.perf_counter() - t0) / iterations * 1000

        # 7. Full current implementation (shadow + main)
        shadow_pen = QPen(QColor(0, 0, 0))
        shadow_pen.setWidthF(5.0)
        shadow_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        shadow_pen.setJoinStyle(Qt.PenJoinStyle.BevelJoin)

        for _ in range(warmup):
            painter = QPainter(image)
            # Shadow (no AA)
            painter.setPen(shadow_pen)
            painter.drawPath(path)
            # Main (with AA)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(pen)
            painter.drawPath(path)
            painter.end()

        t0 = time.perf_counter()
        for _ in range(iterations):
            painter = QPainter(image)
            painter.setPen(shadow_pen)
            painter.drawPath(path)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(pen)
            painter.drawPath(path)
            painter.end()
        results["shadow + main (current)"] = (time.perf_counter() - t0) / iterations * 1000

        # 8. Pre-built points array (avoid list(history))
        # Pre-allocate points array once, reuse it
        pre_points = [QPointF(0, 0) for _ in range(60)]

        def update_points_inplace():
            for i in range(n):
                pre_points[i].setX(i * x_step)
                pre_points[i].setY(height - values[i] * y_scale)

        for _ in range(warmup):
            update_points_inplace()

        t0 = time.perf_counter()
        for _ in range(iterations):
            update_points_inplace()
        results["update pre-alloc points"] = (time.perf_counter() - t0) / iterations * 1000

        # 9. Compare: reconstruct path from pre-alloc points
        for _ in range(warmup):
            path2 = QPainterPath()
            path2.moveTo(pre_points[0])
            for i in range(1, n):
                path2.lineTo(pre_points[i])

        t0 = time.perf_counter()
        for _ in range(iterations):
            path2 = QPainterPath()
            path2.moveTo(pre_points[0])
            for i in range(1, n):
                path2.lineTo(pre_points[i])
        results["path from pre-alloc"] = (time.perf_counter() - t0) / iterations * 1000

        # Print results
        print("\n")
        print("=" * 70)
        print("LINE DRAWING MICRO-BENCHMARK")
        print("=" * 70)
        print(f"Plot size: {width}x{height}, Points: {n}")
        print(f"Iterations: {iterations}")
        print()
        print(f"{'Component':<30} {'Time (ms)':<12} {'Notes':<30}")
        print("-" * 70)

        for name, time_ms in sorted(results.items(), key=lambda x: x[1], reverse=True):
            notes = ""
            if name == "drawPath (with AA)":
                notes = "<-- rendering bottleneck"
            elif name == "shadow + main (current)":
                notes = "<-- current implementation"
            print(f"{name:<30} {time_ms:<12.4f} {notes}")

        print()
        print("Key insights:")
        aa_overhead = results['drawPath (with AA)'] - results['drawPath (no AA)']
        shadow_adds = results['shadow + main (current)'] - results['drawPath (with AA)']
        poly_vs_path = results['drawPolyline (with AA)'] - results['drawPath (with AA)']
        path_pct = results['path construction'] / results['shadow + main (current)'] * 100
        print(f"  - Antialiasing overhead: {aa_overhead:.3f}ms")
        print(f"  - Shadow adds: {shadow_adds:.3f}ms")
        print(f"  - Polyline vs Path: {poly_vs_path:.3f}ms")
        path_ms = results['path construction']
        print(f"  - Path construction: {path_ms:.3f}ms ({path_pct:.0f}% of total)")
        print("=" * 70)
