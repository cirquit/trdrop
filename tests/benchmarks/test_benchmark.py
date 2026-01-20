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
from trdrop import __engine_version__
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.compositor import ScaleMode
from trdrop.compositor.overlay import FPSText, FrameratePlot, FrametimePlot, PlotStyle
from trdrop.compositor.overlay.text import TextStyle
from trdrop.compositor.simple import SimpleCompositor
from trdrop.engine import StreamingEngine
from trdrop.export import StreamingCSVExporter, StreamingVideoExporter
from trdrop.profiling.profiler import OverlapStats, Profiler, get_profiler, reset_profiler
from trdrop.source.sequential import SequentialFrameSource
from trdrop.video.reader import PyAVReader

# Benchmark constants
WARMUP_FRAMES = 5  # Skip first N frames for JIT warmup
DURATION_SEC = 2.0
OUTPUT_RES = (1920, 1080)
SOURCE_RES = (1280, 720)


@pytest.fixture(scope="module")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app  # type: ignore[return-value]


def _create_styles() -> tuple[PlotStyle, TextStyle]:
    """Create minimal overlay styles."""
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


def _run_pipeline(
    tmp_path: Path,
    video_count: int,
    duration_sec: float = DURATION_SEC,
    synchronous: bool = True,
) -> dict:
    """Run full pipeline and return timing results."""
    # Create test videos with varying content fps
    video_paths = []
    content_fps_list = [60, 30, 24, 20]
    for i in range(video_count):
        path = tmp_path / f"source_{i}.mp4"
        VideoGenerator(VideoConfig(
            container_fps=60,
            content_fps=content_fps_list[i % 4],
            duration_sec=duration_sec,
            width=SOURCE_RES[0],
            height=SOURCE_RES[1],
            pattern=PatternType.NUMBER,
            seed=42 + i,
        )).write(path)
        video_paths.append(path)

    readers = [PyAVReader(p) for p in video_paths]
    sources = [SequentialFrameSource(r) for r in readers]
    plot_style, text_style = _create_styles()

    compositor = SimpleCompositor(
        video_count=video_count,
        video_fps=[r.fps for r in readers],
        output_width=OUTPUT_RES[0],
        output_height=OUTPUT_RES[1],
        scale_mode=ScaleMode.CROP,
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
        ],
    )

    output_video = tmp_path / "output.mp4"
    output_csv = tmp_path / "metrics.csv"

    engine = StreamingEngine(
        sources=sources,  # type: ignore[arg-type]
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

    # Extract stats from profiler, skipping warmup frames
    read_ms = analysis_ms = compose_ms = overlay_ms = 0.0
    export_video_ms = export_csv_ms = 0.0
    overlap_stats = OverlapStats()

    if isinstance(profiler, Profiler) and profiler._frames:
        warmup = min(WARMUP_FRAMES, len(profiler._frames) // 10)
        frames = profiler._frames[warmup:]
        n = len(frames)
        if n > 0:
            read_ms = sum(f.read_total_ms for f in frames) / n
            analysis_ms = sum(f.analysis_total_ms for f in frames) / n
            compose_ms = sum(f.compositor_compose_ms for f in frames) / n
            overlay_ms = sum(f.compositor_overlay_ms for f in frames) / n
            export_video_ms = sum(f.export_video_total_ms for f in frames) / n
            export_csv_ms = sum(f.export_csv_ms for f in frames) / n
        overlap_stats = profiler._compute_overlap_stats()

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
        "overlap_stats": overlap_stats,
    }


class TestBenchmark:
    """Pipeline performance benchmark suite."""

    def test_benchmark(self, qapp, tmp_path):
        """Consolidated benchmark: scaling + async comparison."""
        print("\n")
        print("=" * 70)
        print(f"TRDROP BENCHMARK (engine v{__engine_version__})")
        print("=" * 70)
        print(f"Config: {OUTPUT_RES[0]}x{OUTPUT_RES[1]} output, "
              f"{SOURCE_RES[0]}x{SOURCE_RES[1]} sources, {DURATION_SEC}s")
        print()

        # === Multi-video scaling ===
        print("Video Scaling (sync mode):")
        print(f"{'N':<3} {'FPS':>6} {'ms/fr':>7}  "
              f"{'Read':>6} {'Anlyz':>6} {'Comps':>6} {'Ovrly':>6} {'VidEx':>6}")
        print("-" * 70)

        results = []
        for n in [1, 2, 3, 4]:
            reset_profiler()
            r = _run_pipeline(tmp_path / f"bench_{n}", n)
            results.append(r)
            print(f"{n:<3} {r['fps']:>6.1f} {r['ms_per_frame']:>7.1f}  "
                  f"{r['read_ms']:>6.2f} {r['analysis_ms']:>6.2f} "
                  f"{r['compose_ms']:>6.2f} {r['overlay_ms']:>6.2f} "
                  f"{r['export_video_ms']:>6.2f}")

        # Scaling summary
        base_fps = results[0]["fps"]
        print()
        print("Scaling: ", end="")
        for r in results:
            slowdown = base_fps / r["fps"] if r["fps"] > 0 else 0
            print(f"{r['video_count']}v={slowdown:.2f}x  ", end="")
        print()

        # === Sync vs Async comparison ===
        print()
        print("-" * 70)
        print("Sync vs Async (1 video, 3s):")

        reset_profiler()
        sync = _run_pipeline(tmp_path / "sync", 1, duration_sec=3.0, synchronous=True)
        reset_profiler()
        async_ = _run_pipeline(tmp_path / "async", 1, duration_sec=3.0, synchronous=False)

        speedup = sync["total_sec"] / async_["total_sec"]
        overlap = async_["overlap_stats"]

        print(f"  Sync:  {sync['fps']:.1f} fps, {sync['ms_per_frame']:.2f} ms/frame")
        print(f"  Async: {async_['fps']:.1f} fps, {async_['ms_per_frame']:.2f} ms/frame")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Overlap: read={overlap.read_during_prev_export_pct:.0f}%, "
              f"analysis={overlap.analysis_during_prev_export_pct:.0f}%")
        print("=" * 70)

        # Sanity checks
        assert results[0]["fps"] > 0, "Single video benchmark failed"
        assert results[-1]["fps"] > 0, "4-video benchmark failed"
        slowdown_4v = base_fps / results[-1]["fps"]
        assert slowdown_4v < 10, f"4-video slowdown too high: {slowdown_4v:.1f}x"
