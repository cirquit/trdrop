"""Visual comparison of AA strategies - saves images for inspection.

Run with: uv run pytest tests/benchmarks/test_aa_visual.py -v -s
Output: /tmp/aa_comparison_*.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from numba import jit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPainterPath, QPen


@pytest.fixture(scope="module")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app  # type: ignore[return-value]


@jit(nopython=True, cache=True)
def _wu_line(img: np.ndarray, x0: float, y0: float, x1: float, y1: float,
             r: int, g: int, b: int) -> None:
    """Draw anti-aliased line using Xiaolin Wu's algorithm."""
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

    # First endpoint
    xend = round(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = 1.0 - ((x0 + 0.5) % 1.0)
    xpxl1 = int(xend)
    ypxl1 = int(yend)

    if steep:
        frac = 1.0 - (yend % 1.0)
        if 0 <= ypxl1 < w and 0 <= xpxl1 < h:
            img[xpxl1, ypxl1, 0] = min(255, img[xpxl1, ypxl1, 0] + int(b * frac * xgap))
            img[xpxl1, ypxl1, 1] = min(255, img[xpxl1, ypxl1, 1] + int(g * frac * xgap))
            img[xpxl1, ypxl1, 2] = min(255, img[xpxl1, ypxl1, 2] + int(r * frac * xgap))
            img[xpxl1, ypxl1, 3] = 255
        frac = yend % 1.0
        if 0 <= ypxl1 + 1 < w and 0 <= xpxl1 < h:
            img[xpxl1, ypxl1 + 1, 0] = min(255, img[xpxl1, ypxl1 + 1, 0] + int(b * frac * xgap))
            img[xpxl1, ypxl1 + 1, 1] = min(255, img[xpxl1, ypxl1 + 1, 1] + int(g * frac * xgap))
            img[xpxl1, ypxl1 + 1, 2] = min(255, img[xpxl1, ypxl1 + 1, 2] + int(r * frac * xgap))
            img[xpxl1, ypxl1 + 1, 3] = 255
    else:
        frac = 1.0 - (yend % 1.0)
        if 0 <= xpxl1 < w and 0 <= ypxl1 < h:
            img[ypxl1, xpxl1, 0] = min(255, img[ypxl1, xpxl1, 0] + int(b * frac * xgap))
            img[ypxl1, xpxl1, 1] = min(255, img[ypxl1, xpxl1, 1] + int(g * frac * xgap))
            img[ypxl1, xpxl1, 2] = min(255, img[ypxl1, xpxl1, 2] + int(r * frac * xgap))
            img[ypxl1, xpxl1, 3] = 255
        frac = yend % 1.0
        if 0 <= xpxl1 < w and 0 <= ypxl1 + 1 < h:
            img[ypxl1 + 1, xpxl1, 0] = min(255, img[ypxl1 + 1, xpxl1, 0] + int(b * frac * xgap))
            img[ypxl1 + 1, xpxl1, 1] = min(255, img[ypxl1 + 1, xpxl1, 1] + int(g * frac * xgap))
            img[ypxl1 + 1, xpxl1, 2] = min(255, img[ypxl1 + 1, xpxl1, 2] + int(r * frac * xgap))
            img[ypxl1 + 1, xpxl1, 3] = 255

    intery = yend + gradient

    # Second endpoint
    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = (x1 + 0.5) % 1.0
    xpxl2 = int(xend)

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
                img[x, yi, 3] = 255
            if 0 <= yi + 1 < w and 0 <= x < h:
                img[x, yi + 1, 0] = min(255, img[x, yi + 1, 0] + int(b * frac_lo))
                img[x, yi + 1, 1] = min(255, img[x, yi + 1, 1] + int(g * frac_lo))
                img[x, yi + 1, 2] = min(255, img[x, yi + 1, 2] + int(r * frac_lo))
                img[x, yi + 1, 3] = 255
        else:
            if 0 <= x < w and 0 <= yi < h:
                img[yi, x, 0] = min(255, img[yi, x, 0] + int(b * frac_hi))
                img[yi, x, 1] = min(255, img[yi, x, 1] + int(g * frac_hi))
                img[yi, x, 2] = min(255, img[yi, x, 2] + int(r * frac_hi))
                img[yi, x, 3] = 255
            if 0 <= x < w and 0 <= yi + 1 < h:
                img[yi + 1, x, 0] = min(255, img[yi + 1, x, 0] + int(b * frac_lo))
                img[yi + 1, x, 1] = min(255, img[yi + 1, x, 1] + int(g * frac_lo))
                img[yi + 1, x, 2] = min(255, img[yi + 1, x, 2] + int(r * frac_lo))
                img[yi + 1, x, 3] = 255

        intery += gradient


@jit(nopython=True, cache=True)
def draw_polyline_wu(img: np.ndarray, xs: np.ndarray, ys: np.ndarray,
                     r: int, g: int, b: int) -> None:
    """Draw anti-aliased polyline."""
    n = len(xs)
    for i in range(n - 1):
        _wu_line(img, xs[i], ys[i], xs[i + 1], ys[i + 1], r, g, b)


@jit(nopython=True, cache=True)
def draw_polyline_wu_thick(img: np.ndarray, xs: np.ndarray, ys: np.ndarray,
                           r: int, g: int, b: int, thickness: int) -> None:
    """Draw thick anti-aliased polyline using multiple offset Wu lines."""
    half = thickness // 2
    # Draw multiple passes with offsets to create thickness
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            # Use circular pattern for smoother edges
            if dx * dx + dy * dy <= half * half + half:
                draw_polyline_wu(img, xs + dx, ys + dy, r, g, b)


class TestAAVisual:
    """Generate visual comparison images."""

    def test_generate_comparison(self, qapp, tmp_path):
        """Generate comparison images for visual inspection."""
        width, height = 400, 100
        n_points = 30

        # Generate wavy line data
        xs = np.linspace(20, width - 20, n_points)
        ys = 50 + 30 * np.sin(np.linspace(0, 4 * np.pi, n_points))

        output_dir = Path("/tmp")

        # ================================================================
        # 1. QPainter with AA (reference)
        # ================================================================
        image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(QColor(40, 40, 40))

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

        p = QPainter(image)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

        image.save(str(output_dir / "aa_1_qpainter_aa.png"))

        # ================================================================
        # 2. QPainter without AA
        # ================================================================
        image.fill(QColor(40, 40, 40))
        p = QPainter(image)
        p.setPen(pen)
        p.drawPath(path)
        p.end()
        image.save(str(output_dir / "aa_2_qpainter_no_aa.png"))

        # ================================================================
        # 3. Numba Wu 1px
        # ================================================================
        img_np = np.zeros((height, width, 4), dtype=np.uint8)
        img_np[:, :, :3] = 40  # Dark gray background
        img_np[:, :, 3] = 255

        draw_polyline_wu(img_np, xs, ys, 255, 100, 200)

        qimg = QImage(img_np.data, width, height, width * 4,
                      QImage.Format.Format_RGBA8888)
        qimg.save(str(output_dir / "aa_3_numba_wu_1px.png"))

        # ================================================================
        # 4. Numba Wu thick (3px)
        # ================================================================
        img_np = np.zeros((height, width, 4), dtype=np.uint8)
        img_np[:, :, :3] = 40
        img_np[:, :, 3] = 255

        draw_polyline_wu_thick(img_np, xs, ys, 255, 100, 200, 3)

        qimg = QImage(img_np.data, width, height, width * 4,
                      QImage.Format.Format_RGBA8888)
        qimg.save(str(output_dir / "aa_4_numba_wu_thick.png"))

        # ================================================================
        # 5. Combined comparison image
        # ================================================================
        combined = QImage(width, height * 4 + 30, QImage.Format.Format_ARGB32_Premultiplied)
        combined.fill(QColor(30, 30, 30))

        p = QPainter(combined)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        labels = [
            "QPainter AA (current)",
            "QPainter no AA",
            "Numba Wu 1px",
            "Numba Wu thick 3px"
        ]

        for i, label in enumerate(labels):
            y_offset = i * (height + 5) + 15
            # Load and draw the image
            img_path = output_dir / f"aa_{i+1}_*.png"
            # Draw label
            p.setPen(QColor(200, 200, 200))
            p.drawText(10, y_offset - 2, label)

        p.end()

        print(f"\nComparison images saved to {output_dir}/aa_*.png")
        print("Open these files to visually compare AA quality:")
        print("  - aa_1_qpainter_aa.png (reference)")
        print("  - aa_2_qpainter_no_aa.png")
        print("  - aa_3_numba_wu_1px.png")
        print("  - aa_4_numba_wu_thick.png")
