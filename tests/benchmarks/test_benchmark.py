"""Pipeline performance benchmark.

Run with: make benchmark
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest
from PyQt6.QtGui import QColor, QFont, QGuiApplication

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.compositor import ScaleMode
from trdrop.compositor.overlay import FrameratePlot, FrametimePlot, FPSText, PlotStyle
from trdrop.compositor.overlay.text import TextStyle
from trdrop.compositor.simple import SimpleCompositor
from trdrop.engine import StreamingEngine
from trdrop.export import StreamingCSVExporter, StreamingVideoExporter
from trdrop.profiling.profiler import get_profiler, Profiler
from trdrop.source.sequential import SequentialFrameSource
from trdrop.video.reader import PyAVReader


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


def run_pipeline(
    tmp_path: Path,
    video_count: int,
    duration_sec: float = 2.0,
    synchronous: bool = True,
    scale_mode: ScaleMode = ScaleMode.CROP,
    include_frametime: bool = True,
) -> dict:
    """Run full pipeline with default settings and return timing results."""
    # Create test videos
    video_paths = []
    for i in range(video_count):
        path = tmp_path / f"source_{i}.mp4"
        VideoGenerator(VideoConfig(
            container_fps=60,
            content_fps=[60, 30, 24, 20][i % 4],  # Varying content fps
            duration_sec=duration_sec,
            width=1280,
            height=720,
            pattern=PatternType.NUMBER,
            seed=42 + i,
        )).write(path)
        video_paths.append(path)

    readers = [PyAVReader(p) for p in video_paths]
    sources = [SequentialFrameSource(r) for r in readers]
    plot_style, text_style = create_styles()

    # Full default config: FPS text, framerate plot, frametime plot (optional)
    compositor = SimpleCompositor(
        video_count=video_count,
        video_fps=[r.fps for r in readers],
        output_width=1920,
        output_height=1080,
        scale_mode=scale_mode,
        fps_texts=[FPSText(text_style, prefix="FPS:") for _ in range(video_count)],
        framerate_plots=[
            FrameratePlot(plot_style, max_fps=60.0, time_anchor=0.5,
                         show_time_indicator=True, show_start_marker=True)
            for _ in range(video_count)
        ],
        frametime_plots=[
            FrametimePlot(plot_style, max_ms=50.0, auto_scale=True,
                         show_current_value=True, time_anchor=0.5,
                         show_time_indicator=True, show_start_marker=True)
            for _ in range(video_count)
        ] if include_frametime else None,
    )

    output_video = tmp_path / "output.mp4"
    output_csv = tmp_path / "metrics.csv"

    engine = StreamingEngine(
        sources=sources,
        analyzers=[DuplicateDetector()],
        compositor=compositor,
        exporters=[
            StreamingVideoExporter(output_video, fps=readers[0].fps,
                                   codec="libx264", crf=23, preset="ultrafast"),
            StreamingCSVExporter(output_csv),
        ],
        synchronous=synchronous,
    )

    profiler = get_profiler()
    start = time.perf_counter()
    engine.run()
    total_sec = time.perf_counter() - start

    total_frames = int(60 * duration_sec) - 1

    # Extract stats from profiler's internal frame data
    read_ms = 0.0
    analysis_ms = 0.0
    compose_ms = 0.0
    overlay_ms = 0.0
    export_video_ms = 0.0
    export_csv_ms = 0.0

    if isinstance(profiler, Profiler) and profiler._frames:
        frames = profiler._frames
        n = len(frames)
        read_ms = sum(f.read_total_ms for f in frames) / n
        analysis_ms = sum(f.analysis_total_ms for f in frames) / n
        compose_ms = sum(f.compositor_compose_ms for f in frames) / n
        overlay_ms = sum(f.compositor_overlay_ms for f in frames) / n
        export_video_ms = sum(f.export_video_total_ms for f in frames) / n
        export_csv_ms = sum(f.export_csv_ms for f in frames) / n

    return {
        "video_count": video_count,
        "total_frames": total_frames,
        "total_sec": total_sec,
        "fps": total_frames / total_sec,
        "ms_per_frame": (total_sec / total_frames) * 1000,
        "read_ms": read_ms,
        "analysis_ms": analysis_ms,
        "compose_ms": compose_ms,
        "overlay_ms": overlay_ms,
        "export_video_ms": export_video_ms,
        "export_csv_ms": export_csv_ms,
    }


class TestBenchmark:
    """Pipeline performance benchmark suite."""

    def test_benchmark_summary(self, qapp, tmp_path):
        """Run complete benchmark and print summary table."""
        from trdrop.profiling.profiler import reset_profiler

        print("\n")
        print("=" * 80)
        print("TRDROP PIPELINE BENCHMARK")
        print("=" * 80)
        print("Config: 1920x1080 output, 1280x720 sources, 2s duration, full overlays")
        print()

        results = []
        for n in [1, 2, 3, 4]:
            reset_profiler()
            r = run_pipeline(tmp_path / f"bench_{n}", n)
            results.append(r)

        # Header
        print(f"{'Videos':<8} {'FPS':<8} {'ms/fr':<8} "
              f"{'Read':<8} {'Analyze':<8} {'Compose':<9} {'Overlay':<9} "
              f"{'VidExp':<8} {'CSVExp':<8}")
        print("-" * 80)

        # Data rows
        for r in results:
            print(f"{r['video_count']:<8} "
                  f"{r['fps']:<8.1f} "
                  f"{r['ms_per_frame']:<8.1f} "
                  f"{r['read_ms']:<8.2f} "
                  f"{r['analysis_ms']:<8.2f} "
                  f"{r['compose_ms']:<9.2f} "
                  f"{r['overlay_ms']:<9.2f} "
                  f"{r['export_video_ms']:<8.2f} "
                  f"{r['export_csv_ms']:<8.2f}")

        # Scaling analysis
        print()
        print("Scaling (relative to 1 video):")
        base_fps = results[0]["fps"]
        for r in results:
            slowdown = base_fps / r["fps"] if r["fps"] > 0 else 0
            print(f"  {r['video_count']} videos: {slowdown:.2f}x")

        # Async comparison
        print()
        print("-" * 80)
        print("Async Export Comparison (1 video, 3s):")
        reset_profiler()
        sync = run_pipeline(tmp_path / "sync", 1, duration_sec=3.0, synchronous=True)
        reset_profiler()
        async_ = run_pipeline(tmp_path / "async", 1, duration_sec=3.0, synchronous=False)

        speedup = sync["total_sec"] / async_["total_sec"]
        overlap_ms = (sync["ms_per_frame"] - async_["ms_per_frame"])
        export_ms = sync["export_video_ms"]
        overlap_pct = (overlap_ms / export_ms * 100) if export_ms > 0 else 0

        print(f"  Sync:  {sync['fps']:.1f} fps, {sync['ms_per_frame']:.2f} ms/frame")
        print(f"  Async: {async_['fps']:.1f} fps, {async_['ms_per_frame']:.2f} ms/frame")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Pipeline overlap: {overlap_pct:.0f}% of export time ({overlap_ms:.2f} ms)")
        print("=" * 80)

        # Sanity checks
        assert results[0]["fps"] > 0
        assert results[-1]["fps"] > 0
        slowdown_4v = base_fps / results[-1]["fps"]
        assert slowdown_4v < 10, f"4-video slowdown too high: {slowdown_4v:.1f}x"

    def test_scale_mode_comparison(self, qapp, tmp_path):
        """Compare CROP vs FIT scale modes."""
        from trdrop.profiling.profiler import reset_profiler

        print("\n")
        print("=" * 80)
        print("SCALE MODE COMPARISON")
        print("=" * 80)
        print("Config: 1920x1080 output, 1280x720 sources, 2s duration, full overlays")
        print()

        # Run benchmarks for both modes
        all_results = {}
        for mode in [ScaleMode.CROP, ScaleMode.FIT]:
            mode_results = []
            for n in [1, 2, 3, 4]:
                reset_profiler()
                r = run_pipeline(tmp_path / f"{mode.name}_{n}", n, scale_mode=mode)
                mode_results.append(r)
            all_results[mode.name] = mode_results

        # Print comparison table
        print(f"{'Mode':<6} {'Vid':<4} {'FPS':<7} {'ms/fr':<7} "
              f"{'Read':<7} {'Analyze':<8} {'Compose':<8} {'Overlay':<8} "
              f"{'VidExp':<7}")
        print("-" * 80)

        for mode_name in ["CROP", "FIT"]:
            for r in all_results[mode_name]:
                print(f"{mode_name:<6} "
                      f"{r['video_count']:<4} "
                      f"{r['fps']:<7.1f} "
                      f"{r['ms_per_frame']:<7.1f} "
                      f"{r['read_ms']:<7.2f} "
                      f"{r['analysis_ms']:<8.2f} "
                      f"{r['compose_ms']:<8.2f} "
                      f"{r['overlay_ms']:<8.2f} "
                      f"{r['export_video_ms']:<7.2f}")
            print()

        # Speedup summary
        print("CROP vs FIT Speedup:")
        for i, n in enumerate([1, 2, 3, 4]):
            crop_fps = all_results["CROP"][i]["fps"]
            fit_fps = all_results["FIT"][i]["fps"]
            speedup = crop_fps / fit_fps if fit_fps > 0 else 0
            print(f"  {n} video(s): CROP {crop_fps:.1f} fps vs FIT {fit_fps:.1f} fps = {speedup:.2f}x faster")
        print("=" * 80)
