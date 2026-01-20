"""Benchmark different anti-aliasing strategies for line drawing.

Compares:
1. QPainter with AA (current)
2. QPainter without AA
3. 2x render + downsample (poor man's AA)
4. Numba Wu's algorithm (1px line)
5. Numba thick line via dilation

Run with: uv run pytest tests/benchmarks/test_aa_strategies.py -v -s
"""

from __future__ import annotations

import sys
import time

import numpy as np
import pytest
from numba import jit
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

from trdrop.utils.ringbuffer import RingBuffer


@pytest.fixture(scope="module")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app  # type: ignore[return-value]


# ============================================================================
# Numba-accelerated line drawing
# ============================================================================

@jit(nopython=True, cache=True)
def _wu_line(img: np.ndarray, x0: float, y0: float, x1: float, y1: float,
             r: int, g: int, b: int, a: int) -> None:
    """Draw anti-aliased line using Xiaolin Wu's algorithm.

    Draws a 1-pixel wide AA line into an ARGB32 image buffer.
    """
    h, w = img.shape[:2]

    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 1.0

    # Handle first endpoint
    xend = round(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = 1.0 - ((x0 + 0.5) % 1.0)
    xpxl1 = int(xend)
    ypxl1 = int(yend)

    if steep:
        if 0 <= ypxl1 < w and 0 <= xpxl1 < h:
            frac = (1.0 - (yend % 1.0)) * xgap
            img[xpxl1, ypxl1, 0] = min(255, img[xpxl1, ypxl1, 0] + int(b * frac))
            img[xpxl1, ypxl1, 1] = min(255, img[xpxl1, ypxl1, 1] + int(g * frac))
            img[xpxl1, ypxl1, 2] = min(255, img[xpxl1, ypxl1, 2] + int(r * frac))
        if 0 <= ypxl1 + 1 < w and 0 <= xpxl1 < h:
            frac = (yend % 1.0) * xgap
            img[xpxl1, ypxl1 + 1, 0] = min(255, img[xpxl1, ypxl1 + 1, 0] + int(b * frac))
            img[xpxl1, ypxl1 + 1, 1] = min(255, img[xpxl1, ypxl1 + 1, 1] + int(g * frac))
            img[xpxl1, ypxl1 + 1, 2] = min(255, img[xpxl1, ypxl1 + 1, 2] + int(r * frac))
    else:
        if 0 <= xpxl1 < w and 0 <= ypxl1 < h:
            frac = (1.0 - (yend % 1.0)) * xgap
            img[ypxl1, xpxl1, 0] = min(255, img[ypxl1, xpxl1, 0] + int(b * frac))
            img[ypxl1, xpxl1, 1] = min(255, img[ypxl1, xpxl1, 1] + int(g * frac))
            img[ypxl1, xpxl1, 2] = min(255, img[ypxl1, xpxl1, 2] + int(r * frac))
        if 0 <= xpxl1 < w and 0 <= ypxl1 + 1 < h:
            frac = (yend % 1.0) * xgap
            img[ypxl1 + 1, xpxl1, 0] = min(255, img[ypxl1 + 1, xpxl1, 0] + int(b * frac))
            img[ypxl1 + 1, xpxl1, 1] = min(255, img[ypxl1 + 1, xpxl1, 1] + int(g * frac))
            img[ypxl1 + 1, xpxl1, 2] = min(255, img[ypxl1 + 1, xpxl1, 2] + int(r * frac))

    intery = yend + gradient

    # Handle second endpoint
    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = (x1 + 0.5) % 1.0
    xpxl2 = int(xend)
    ypxl2 = int(yend)

    if steep:
        if 0 <= ypxl2 < w and 0 <= xpxl2 < h:
            frac = (1.0 - (yend % 1.0)) * xgap
            img[xpxl2, ypxl2, 0] = min(255, img[xpxl2, ypxl2, 0] + int(b * frac))
            img[xpxl2, ypxl2, 1] = min(255, img[xpxl2, ypxl2, 1] + int(g * frac))
            img[xpxl2, ypxl2, 2] = min(255, img[xpxl2, ypxl2, 2] + int(r * frac))
        if 0 <= ypxl2 + 1 < w and 0 <= xpxl2 < h:
            frac = (yend % 1.0) * xgap
            img[xpxl2, ypxl2 + 1, 0] = min(255, img[xpxl2, ypxl2 + 1, 0] + int(b * frac))
            img[xpxl2, ypxl2 + 1, 1] = min(255, img[xpxl2, ypxl2 + 1, 1] + int(g * frac))
            img[xpxl2, ypxl2 + 1, 2] = min(255, img[xpxl2, ypxl2 + 1, 2] + int(r * frac))
    else:
        if 0 <= xpxl2 < w and 0 <= ypxl2 < h:
            frac = (1.0 - (yend % 1.0)) * xgap
            img[ypxl2, xpxl2, 0] = min(255, img[ypxl2, xpxl2, 0] + int(b * frac))
            img[ypxl2, xpxl2, 1] = min(255, img[ypxl2, xpxl2, 1] + int(g * frac))
            img[ypxl2, xpxl2, 2] = min(255, img[ypxl2, xpxl2, 2] + int(r * frac))
        if 0 <= xpxl2 < w and 0 <= ypxl2 + 1 < h:
            frac = (yend % 1.0) * xgap
            img[ypxl2 + 1, xpxl2, 0] = min(255, img[ypxl2 + 1, xpxl2, 0] + int(b * frac))
            img[ypxl2 + 1, xpxl2, 1] = min(255, img[ypxl2 + 1, xpxl2, 1] + int(g * frac))
            img[ypxl2 + 1, xpxl2, 2] = min(255, img[ypxl2 + 1, xpxl2, 2] + int(r * frac))

    # Main loop
    for x in range(xpxl1 + 1, xpxl2):
        yi = int(intery)
        frac_hi = 1.0 - (intery % 1.0)
        frac_lo = intery % 1.0

        if steep:
            if 0 <= yi < w and 0 <= x < h:
                img[x, yi, 0] = min(255, img[x, yi, 0] + int(b * frac_hi))
                img[x, yi, 1] = min(255, img[x, yi, 1] + int(g * frac_hi))
                img[x, yi, 2] = min(255, img[x, yi, 2] + int(r * frac_hi))
            if 0 <= yi + 1 < w and 0 <= x < h:
                img[x, yi + 1, 0] = min(255, img[x, yi + 1, 0] + int(b * frac_lo))
                img[x, yi + 1, 1] = min(255, img[x, yi + 1, 1] + int(g * frac_lo))
                img[x, yi + 1, 2] = min(255, img[x, yi + 1, 2] + int(r * frac_lo))
        else:
            if 0 <= x < w and 0 <= yi < h:
                img[yi, x, 0] = min(255, img[yi, x, 0] + int(b * frac_hi))
                img[yi, x, 1] = min(255, img[yi, x, 1] + int(g * frac_hi))
                img[yi, x, 2] = min(255, img[yi, x, 2] + int(r * frac_hi))
            if 0 <= x < w and 0 <= yi + 1 < h:
                img[yi + 1, x, 0] = min(255, img[yi + 1, x, 0] + int(b * frac_lo))
                img[yi + 1, x, 1] = min(255, img[yi + 1, x, 1] + int(g * frac_lo))
                img[yi + 1, x, 2] = min(255, img[yi + 1, x, 2] + int(r * frac_lo))

        intery += gradient


@jit(nopython=True, cache=True)
def _draw_polyline_wu(img: np.ndarray, xs: np.ndarray, ys: np.ndarray,
                      r: int, g: int, b: int, a: int) -> None:
    """Draw anti-aliased polyline using Wu's algorithm."""
    n = len(xs)
    for i in range(n - 1):
        _wu_line(img, xs[i], ys[i], xs[i + 1], ys[i + 1], r, g, b, a)


@jit(nopython=True, cache=True)
def _draw_thick_line_bresenham(img: np.ndarray, x0: int, y0: int, x1: int, y1: int,
                                r: int, g: int, b: int, thickness: int) -> None:
    """Draw thick line using Bresenham with perpendicular expansion."""
    h, w = img.shape[:2]
    half = thickness // 2

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        # Draw a filled circle at each point for thickness
        for dy2 in range(-half, half + 1):
            for dx2 in range(-half, half + 1):
                if dx2 * dx2 + dy2 * dy2 <= half * half:
                    px, py = x0 + dx2, y0 + dy2
                    if 0 <= px < w and 0 <= py < h:
                        img[py, px, 0] = b
                        img[py, px, 1] = g
                        img[py, px, 2] = r
                        img[py, px, 3] = 255

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


@jit(nopython=True, cache=True)
def _draw_polyline_thick(img: np.ndarray, xs: np.ndarray, ys: np.ndarray,
                         r: int, g: int, b: int, thickness: int) -> None:
    """Draw thick polyline using Bresenham."""
    n = len(xs)
    for i in range(n - 1):
        _draw_thick_line_bresenham(
            img, int(xs[i]), int(ys[i]), int(xs[i + 1]), int(ys[i + 1]),
            r, g, b, thickness
        )


class TestAAStrategies:
    """Benchmark different anti-aliasing strategies."""

    def test_aa_comparison(self, qapp):
        """Compare AA strategies for polyline drawing."""
        width, height = 800, 200
        n_points = 60
        iterations = 100
        warmup = 10

        # Generate test data (same as real FPS history)
        values = np.array([30.0 + 15.0 * (i % 10) / 10 for i in range(n_points)])
        x_step = width / (n_points - 1)
        y_scale = height / 60.0

        xs = np.array([i * x_step for i in range(n_points)], dtype=np.float64)
        ys = np.array([height - values[i] * y_scale for i in range(n_points)],
                      dtype=np.float64)

        results = {}

        # ================================================================
        # Strategy 1: QPainter with AA (current implementation)
        # ================================================================
        image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        path = QPainterPath()
        for i in range(n_points):
            if i == 0:
                path.moveTo(xs[i], ys[i])
            else:
                path.lineTo(xs[i], ys[i])

        pen = QPen(QColor(255, 100, 200))
        pen.setWidthF(3.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        for _ in range(warmup):
            image.fill(QColor(0, 0, 0, 0))
            p = QPainter(image)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(pen)
            p.drawPath(path)
            p.end()

        t0 = time.perf_counter()
        for _ in range(iterations):
            image.fill(QColor(0, 0, 0, 0))
            p = QPainter(image)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(pen)
            p.drawPath(path)
            p.end()
        results["QPainter AA"] = (time.perf_counter() - t0) / iterations * 1000

        # ================================================================
        # Strategy 2: QPainter without AA
        # ================================================================
        for _ in range(warmup):
            image.fill(QColor(0, 0, 0, 0))
            p = QPainter(image)
            p.setPen(pen)
            p.drawPath(path)
            p.end()

        t0 = time.perf_counter()
        for _ in range(iterations):
            image.fill(QColor(0, 0, 0, 0))
            p = QPainter(image)
            p.setPen(pen)
            p.drawPath(path)
            p.end()
        results["QPainter no AA"] = (time.perf_counter() - t0) / iterations * 1000

        # ================================================================
        # Strategy 3: 2x render + downsample
        # ================================================================
        image_2x = QImage(width * 2, height * 2, QImage.Format.Format_ARGB32_Premultiplied)
        path_2x = QPainterPath()
        for i in range(n_points):
            if i == 0:
                path_2x.moveTo(xs[i] * 2, ys[i] * 2)
            else:
                path_2x.lineTo(xs[i] * 2, ys[i] * 2)

        pen_2x = QPen(QColor(255, 100, 200))
        pen_2x.setWidthF(6.0)  # 2x thickness
        pen_2x.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_2x.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        for _ in range(warmup):
            image_2x.fill(QColor(0, 0, 0, 0))
            p = QPainter(image_2x)
            p.setPen(pen_2x)
            p.drawPath(path_2x)
            p.end()
            _ = image_2x.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)

        t0 = time.perf_counter()
        for _ in range(iterations):
            image_2x.fill(QColor(0, 0, 0, 0))
            p = QPainter(image_2x)
            p.setPen(pen_2x)
            p.drawPath(path_2x)
            p.end()
            _ = image_2x.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
        results["2x + downsample"] = (time.perf_counter() - t0) / iterations * 1000

        # ================================================================
        # Strategy 4: Numba Wu's algorithm (1px line)
        # ================================================================
        img_np = np.zeros((height, width, 4), dtype=np.uint8)

        # Warmup JIT
        _draw_polyline_wu(img_np, xs, ys, 255, 100, 200, 255)

        for _ in range(warmup):
            img_np.fill(0)
            _draw_polyline_wu(img_np, xs, ys, 255, 100, 200, 255)

        t0 = time.perf_counter()
        for _ in range(iterations):
            img_np.fill(0)
            _draw_polyline_wu(img_np, xs, ys, 255, 100, 200, 255)
        results["Numba Wu 1px"] = (time.perf_counter() - t0) / iterations * 1000

        # ================================================================
        # Strategy 5: Numba thick line (no AA)
        # ================================================================
        # Warmup
        _draw_polyline_thick(img_np, xs, ys, 255, 100, 200, 3)

        for _ in range(warmup):
            img_np.fill(0)
            _draw_polyline_thick(img_np, xs, ys, 255, 100, 200, 3)

        t0 = time.perf_counter()
        for _ in range(iterations):
            img_np.fill(0)
            _draw_polyline_thick(img_np, xs, ys, 255, 100, 200, 3)
        results["Numba thick 3px"] = (time.perf_counter() - t0) / iterations * 1000

        # ================================================================
        # Strategy 6: Numba Wu + thickness via multiple passes
        # ================================================================
        def draw_wu_thick():
            img_np.fill(0)
            # Draw multiple offset lines to simulate thickness
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 or dy == 0:  # Cross pattern for 3px
                        _draw_polyline_wu(img_np, xs + dx, ys + dy, 255, 100, 200, 255)

        draw_wu_thick()  # JIT warmup
        for _ in range(warmup):
            draw_wu_thick()

        t0 = time.perf_counter()
        for _ in range(iterations):
            draw_wu_thick()
        results["Numba Wu thick"] = (time.perf_counter() - t0) / iterations * 1000

        # ================================================================
        # Print results
        # ================================================================
        print("\n")
        print("=" * 70)
        print("ANTI-ALIASING STRATEGY COMPARISON")
        print("=" * 70)
        print(f"Canvas: {width}x{height}, Points: {n_points}, Line width: 3px")
        print(f"Iterations: {iterations}")
        print()
        print(f"{'Strategy':<25} {'Time (ms)':<12} {'vs QPainter AA':<15} {'Notes'}")
        print("-" * 70)

        baseline = results["QPainter AA"]
        for name, time_ms in sorted(results.items(), key=lambda x: x[1]):
            speedup = baseline / time_ms
            notes = ""
            if name == "QPainter AA":
                notes = "current"
            elif name == "QPainter no AA":
                notes = "jaggy"
            elif name == "Numba Wu 1px":
                notes = "thin line"
            elif name == "2x + downsample":
                notes = "good quality"
            print(f"{name:<25} {time_ms:<12.3f} {speedup:<15.2f}x {notes}")

        print("=" * 70)

        # Show quality note
        print()
        print("Quality notes:")
        print("  - QPainter AA: Best quality, smooth curves and joins")
        print("  - 2x + downsample: Good quality, slightly soft")
        print("  - Numba Wu: Good for 1px lines, needs work for thick lines")
        print("  - QPainter no AA / Numba thick: Jaggy edges")
