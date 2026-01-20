"""Overlay performance benchmark.

Run with: uv run pytest tests/benchmarks/test_overlay_perf.py -v -s
"""

from __future__ import annotations

import sys
import time

import numpy as np
import pytest
from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter

from trdrop.compositor.overlay import FPSText, FrameratePlot, FrametimePlot, PlotStyle
from trdrop.compositor.overlay.text import TextStyle
from trdrop.utils.ringbuffer import RingBuffer


@pytest.fixture(scope="module")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app


def create_styles():
    """Create default overlay styles."""
    title_font = QFont("Helvetica Neue", 12)
    title_font.setWeight(QFont.Weight.Bold)

    plot_style = PlotStyle(
        line_color=QColor(255, 100, 200),
        background_color=QColor(0, 0, 0, 120),
        axis_color=QColor(236, 236, 236),
        grid_color=QColor(255, 255, 255, 60),
        text_color=QColor(255, 255, 255),
        shadow_color=QColor(0, 0, 0),
        font=QFont("Helvetica Neue", 10),
        title_font=title_font,
        line_width=2,
        shadow_offset=2,
        show_grid=True,
        show_labels=True,
    )

    fps_font = QFont("Helvetica Neue", 16)
    fps_font.setWeight(QFont.Weight.Bold)

    text_style = TextStyle(
        color=QColor(255, 255, 255),
        shadow_color=QColor(0, 0, 0),
        font=fps_font,
        shadow_offset=2,
    )
    return plot_style, text_style


class TestOverlayPerformance:
    """Benchmark individual overlay components."""

    def test_overlay_breakdown(self, qapp):
        """Profile each overlay component individually."""
        plot_style, text_style = create_styles()

        # Create QImage as backing buffer (1920x1080)
        width, height = 1920, 1080
        qimage = QImage(width, height, QImage.Format.Format_RGB888)
        qimage.fill(0)

        # Create overlay components
        fps_text = FPSText(text_style, prefix="FPS:")
        framerate_plot = FrameratePlot(
            plot_style, max_fps=60.0, time_anchor=0.5,
            show_time_indicator=True, show_start_marker=True
        )
        frametime_plot = FrametimePlot(
            plot_style, max_ms=50.0, auto_scale=True,
            show_current_value=True, time_anchor=0.5,
            show_time_indicator=True, show_start_marker=True
        )

        # Create history buffers with realistic data
        history_size = 60
        fps_history = RingBuffer(size=history_size, dtype=np.float32)
        frametime_history = RingBuffer(size=history_size, dtype=np.float32)

        # Fill with realistic data
        rng = np.random.default_rng(42)
        for _ in range(history_size):
            fps_history.push(30.0 + rng.random() * 30.0)  # 30-60 FPS
            frametime_history.push(16.67 + rng.random() * 16.67)  # 16-33ms

        # Bounds for components
        fps_text_pos = QPoint(100, 100)
        framerate_bounds = QRect(100, 750, 800, 200)
        frametime_bounds = QRect(100, 550, 200, 80)

        n_iterations = 100
        warmup = 10

        # Warmup
        for _ in range(warmup):
            painter = QPainter(qimage)
            fps_text.draw(painter, fps_text_pos, 45.0)
            framerate_plot.draw(painter, framerate_bounds, fps_history)
            frametime_plot.draw(painter, frametime_bounds, frametime_history, current_value=20.0)
            painter.end()

        results = {}

        # Benchmark FPS text
        t0 = time.perf_counter()
        for _ in range(n_iterations):
            painter = QPainter(qimage)
            fps_text.draw(painter, fps_text_pos, 45.0)
            painter.end()
        results["fps_text"] = (time.perf_counter() - t0) / n_iterations * 1000

        # Benchmark framerate plot
        t0 = time.perf_counter()
        for _ in range(n_iterations):
            painter = QPainter(qimage)
            framerate_plot.draw(painter, framerate_bounds, fps_history)
            painter.end()
        results["framerate_plot"] = (time.perf_counter() - t0) / n_iterations * 1000

        # Benchmark frametime plot
        t0 = time.perf_counter()
        for _ in range(n_iterations):
            painter = QPainter(qimage)
            frametime_plot.draw(painter, frametime_bounds, frametime_history, current_value=20.0)
            painter.end()
        results["frametime_plot"] = (time.perf_counter() - t0) / n_iterations * 1000

        # Benchmark all together (what the compositor does)
        t0 = time.perf_counter()
        for _ in range(n_iterations):
            painter = QPainter(qimage)
            fps_text.draw(painter, fps_text_pos, 45.0)
            framerate_plot.draw(painter, framerate_bounds, fps_history)
            frametime_plot.draw(painter, frametime_bounds, frametime_history, current_value=20.0)
            painter.end()
        results["all_combined"] = (time.perf_counter() - t0) / n_iterations * 1000

        # Print results
        print("\n")
        print("=" * 70)
        print("OVERLAY COMPONENT BENCHMARK (1 video)")
        print("=" * 70)
        print(f"Iterations: {n_iterations} (after {warmup} warmup)")
        print()

        print(f"{'Component':<20} {'Time (ms)':<12} {'% of Total':<12}")
        print("-" * 50)

        total = results["all_combined"]
        for name, ms in results.items():
            if name != "all_combined":
                pct = (ms / total) * 100 if total > 0 else 0
                print(f"{name:<20} {ms:<12.3f} {pct:<12.1f}%")

        print("-" * 50)
        print(f"{'all_combined':<20} {total:<12.3f}")
        print("=" * 70)

        # Sanity check
        assert total < 10.0, f"Overlay rendering too slow: {total:.1f}ms"

    def test_plot_operation_breakdown(self, qapp):
        """Profile individual plot operations."""
        plot_style, _ = create_styles()

        width, height = 1920, 1080
        qimage = QImage(width, height, QImage.Format.Format_RGB888)
        qimage.fill(0)

        # Create realistic history
        history_size = 60
        fps_history = RingBuffer(size=history_size, dtype=np.float32)
        rng = np.random.default_rng(42)
        for _ in range(history_size):
            fps_history.push(30.0 + rng.random() * 30.0)

        bounds = QRect(100, 750, 800, 200)

        n_iterations = 100
        warmup = 10

        # Custom plot class to measure individual operations
        class ProfilingPlot(FrameratePlot):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.timings = {
                    "background": [],
                    "grid": [],
                    "line": [],
                    "axes": [],
                    "labels": [],
                    "title": [],
                    "markers": [],
                }

            def draw(self, painter, bounds, history, **kwargs):
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                effective_max = self._get_effective_max(history)

                t0 = time.perf_counter()
                self._draw_background(painter, bounds)
                self.timings["background"].append((time.perf_counter() - t0) * 1000)

                t0 = time.perf_counter()
                self._draw_grid(painter, bounds)
                if self._show_center_line:
                    self._draw_center_line(painter, bounds)
                self.timings["grid"].append((time.perf_counter() - t0) * 1000)

                t0 = time.perf_counter()
                line_points = self._draw_line(painter, bounds, history, effective_max)
                self.timings["line"].append((time.perf_counter() - t0) * 1000)

                t0 = time.perf_counter()
                if line_points and self._show_start_marker:
                    self._draw_start_marker(painter, line_points[0])
                if line_points and self._show_time_indicator:
                    self._draw_time_indicator(painter, bounds, line_points[-1])
                self.timings["markers"].append((time.perf_counter() - t0) * 1000)

                t0 = time.perf_counter()
                self._draw_axes(painter, bounds)
                self.timings["axes"].append((time.perf_counter() - t0) * 1000)

                t0 = time.perf_counter()
                self._draw_labels(painter, bounds, 0.0, effective_max)
                self.timings["labels"].append((time.perf_counter() - t0) * 1000)

                t0 = time.perf_counter()
                self._draw_title(painter, bounds, self._time_anchor)
                self.timings["title"].append((time.perf_counter() - t0) * 1000)

        plot = ProfilingPlot(
            plot_style, max_fps=60.0, time_anchor=0.5,
            show_time_indicator=True, show_start_marker=True
        )

        # Warmup
        for _ in range(warmup):
            painter = QPainter(qimage)
            plot.draw(painter, bounds, fps_history)
            painter.end()

        # Clear warmup timings
        for key in plot.timings:
            plot.timings[key] = []

        # Benchmark
        for _ in range(n_iterations):
            painter = QPainter(qimage)
            plot.draw(painter, bounds, fps_history)
            painter.end()

        # Calculate averages
        print("\n")
        print("=" * 70)
        print("FRAMERATE PLOT OPERATION BREAKDOWN")
        print("=" * 70)
        print(f"Plot size: {bounds.width()}x{bounds.height()}, History: {history_size} points")
        print(f"Iterations: {n_iterations}")
        print()

        print(f"{'Operation':<15} {'Mean (ms)':<12} {'Std (ms)':<12} {'% of Total':<12}")
        print("-" * 55)

        total = 0.0
        avgs = {}
        for name, values in plot.timings.items():
            avg = sum(values) / len(values) if values else 0
            avgs[name] = avg
            total += avg

        # Sort by time
        sorted_ops = sorted(avgs.items(), key=lambda x: -x[1])

        for name, avg in sorted_ops:
            values = plot.timings[name]
            std = np.std(values) if values else 0
            pct = (avg / total) * 100 if total > 0 else 0
            print(f"{name:<15} {avg:<12.4f} {std:<12.4f} {pct:<12.1f}%")

        print("-" * 55)
        print(f"{'TOTAL':<15} {total:<12.4f}")
        print("=" * 70)

    def test_history_size_impact(self, qapp):
        """Test how history size affects rendering time."""
        plot_style, _ = create_styles()

        width, height = 1920, 1080
        qimage = QImage(width, height, QImage.Format.Format_RGB888)
        qimage.fill(0)

        bounds = QRect(100, 750, 800, 200)
        n_iterations = 50
        warmup = 5

        print("\n")
        print("=" * 70)
        print("HISTORY SIZE IMPACT ON PLOT RENDERING")
        print("=" * 70)
        print()

        print(f"{'History Size':<15} {'Time (ms)':<12} {'Points/ms':<12}")
        print("-" * 45)

        for history_size in [30, 60, 120, 240, 480, 960]:
            fps_history = RingBuffer(size=history_size, dtype=np.float32)
            rng = np.random.default_rng(42)
            for _ in range(history_size):
                fps_history.push(30.0 + rng.random() * 30.0)

            plot = FrameratePlot(
                plot_style, max_fps=60.0, time_anchor=0.5,
                show_time_indicator=True, show_start_marker=True
            )

            # Warmup
            for _ in range(warmup):
                painter = QPainter(qimage)
                plot.draw(painter, bounds, fps_history)
                painter.end()

            # Benchmark
            t0 = time.perf_counter()
            for _ in range(n_iterations):
                painter = QPainter(qimage)
                plot.draw(painter, bounds, fps_history)
                painter.end()
            avg_ms = (time.perf_counter() - t0) / n_iterations * 1000
            points_per_ms = history_size / avg_ms if avg_ms > 0 else 0

            print(f"{history_size:<15} {avg_ms:<12.3f} {points_per_ms:<12.1f}")

        print("=" * 70)

    def test_video_count_scaling(self, qapp):
        """Test how overlay time scales with video count."""
        plot_style, text_style = create_styles()

        width, height = 1920, 1080
        qimage = QImage(width, height, QImage.Format.Format_RGB888)

        history_size = 60
        n_iterations = 50
        warmup = 5

        print("\n")
        print("=" * 70)
        print("VIDEO COUNT SCALING (full overlay set per video)")
        print("=" * 70)
        print()

        print(f"{'Videos':<10} {'Time (ms)':<12} {'ms/video':<12} {'Scaling':<12}")
        print("-" * 50)

        baseline_per_video = None

        for video_count in [1, 2, 3, 4]:
            qimage.fill(0)
            video_width = width // video_count

            # Create components and histories for each video
            components = []
            for i in range(video_count):
                fps_text = FPSText(text_style, prefix="FPS:")
                framerate_plot = FrameratePlot(
                    plot_style, max_fps=60.0, time_anchor=0.5,
                    show_time_indicator=True, show_start_marker=True
                )
                frametime_plot = FrametimePlot(
                    plot_style, max_ms=50.0, auto_scale=True,
                    show_current_value=True, time_anchor=0.5,
                    show_time_indicator=True, show_start_marker=True
                )

                fps_history = RingBuffer(size=history_size, dtype=np.float32)
                frametime_history = RingBuffer(size=history_size, dtype=np.float32)
                rng = np.random.default_rng(42 + i)
                for _ in range(history_size):
                    fps_history.push(30.0 + rng.random() * 30.0)
                    frametime_history.push(16.67 + rng.random() * 16.67)

                video_x = i * video_width
                components.append({
                    "fps_text": fps_text,
                    "fps_text_pos": QPoint(video_x + 50, 100),
                    "framerate_plot": framerate_plot,
                    "framerate_bounds": QRect(video_x + 50, height - 250, video_width - 100, 200),
                    "frametime_plot": frametime_plot,
                    "frametime_bounds": QRect(video_x + 50, height - 350, video_width // 4, 80),
                    "fps_history": fps_history,
                    "frametime_history": frametime_history,
                })

            # Warmup
            for _ in range(warmup):
                painter = QPainter(qimage)
                for c in components:
                    c["fps_text"].draw(painter, c["fps_text_pos"], 45.0)
                    c["framerate_plot"].draw(
                        painter, c["framerate_bounds"], c["fps_history"])
                    c["frametime_plot"].draw(
                        painter, c["frametime_bounds"], c["frametime_history"],
                        current_value=20.0)
                painter.end()

            # Benchmark
            t0 = time.perf_counter()
            for _ in range(n_iterations):
                painter = QPainter(qimage)
                for c in components:
                    c["fps_text"].draw(painter, c["fps_text_pos"], 45.0)
                    c["framerate_plot"].draw(
                        painter, c["framerate_bounds"], c["fps_history"])
                    c["frametime_plot"].draw(
                        painter, c["frametime_bounds"], c["frametime_history"],
                        current_value=20.0)
                painter.end()

            avg_ms = (time.perf_counter() - t0) / n_iterations * 1000
            per_video = avg_ms / video_count

            if baseline_per_video is None:
                baseline_per_video = per_video
                scaling = 1.0
            else:
                scaling = per_video / baseline_per_video

            print(f"{video_count:<10} {avg_ms:<12.3f} {per_video:<12.3f} {scaling:<12.2f}x")

        print("=" * 70)
