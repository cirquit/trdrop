"""Benchmark tests for performance tracking.

These tests create consistent test scenarios for measuring pipeline performance
across different video configurations (1-4 videos).

Run with profiling enabled:
    TRDROP_PROFILE=benchmark.csv uv run pytest tests/benchmarks/test_benchmark.py -v

Or via make:
    TRDROP_PROFILE=benchmark.csv make test
"""

from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from PyQt6.QtGui import QColor, QFont, QGuiApplication

from tests.testkit import PatternType, VideoConfig, VideoGenerator


@dataclass
class BenchmarkConfig:
    """Standard benchmark configuration."""

    name: str
    video_count: int
    width: int = 1280
    height: int = 720
    container_fps: int = 60
    content_fps: int = 30
    duration_sec: float = 2.0
    pattern: PatternType = PatternType.NUMBER


# Standard benchmark configurations
BENCHMARK_CONFIGS = [
    BenchmarkConfig(name="single_720p", video_count=1),
    BenchmarkConfig(name="dual_720p", video_count=2),
    BenchmarkConfig(name="triple_720p", video_count=3),
    BenchmarkConfig(name="quad_720p", video_count=4),
]


def print_progress(current: int, total: int, width: int = 40) -> None:
    """Print a portable progress bar that overwrites itself."""
    pct = current / total
    filled = int(width * pct)
    bar = (
        "=" * filled + ">" + " " * (width - filled - 1)
        if filled < width
        else "=" * width
    )
    sys.stdout.write(f"\r  [{bar}] {current}/{total} ({pct * 100:.1f}%)")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")


class TestBenchmarks:
    """Benchmark tests for pipeline performance."""

    @pytest.fixture(scope="class")
    def qapp(self):
        """Create QGuiApplication for font rendering."""
        app = QGuiApplication.instance()
        if app is None:
            app = QGuiApplication(sys.argv)
        return app

    @pytest.fixture
    def reset_profiler(self):
        """Reset the profiler singleton after each test."""
        from trdrop.profiling.profiler import reset_profiler

        yield
        reset_profiler()
        if "TRDROP_PROFILE" in os.environ:
            del os.environ["TRDROP_PROFILE"]

    def _create_test_videos(
        self,
        tmp_path: Path,
        config: BenchmarkConfig,
    ) -> list[Path]:
        """Create test videos for benchmarking."""
        video_paths = []

        for i in range(config.video_count):
            video_path = tmp_path / f"source_{i}.mp4"
            video_config = VideoConfig(
                container_fps=config.container_fps,
                content_fps=config.content_fps,
                duration_sec=config.duration_sec,
                width=config.width,
                height=config.height,
                pattern=config.pattern,
                seed=42 + i,  # Different seed for each video
            )
            VideoGenerator(video_config).write(video_path)
            video_paths.append(video_path)

        return video_paths

    def _run_benchmark(
        self,
        qapp,
        tmp_path: Path,
        config: BenchmarkConfig,
        profile_path: Path | None = None,
        synchronous: bool = True,
    ) -> dict:
        """Run a benchmark and return results."""
        from trdrop.analysis.duplicate import DuplicateDetector
        from trdrop.compositor.overlay import FPSText, FrameratePlot
        from trdrop.compositor.overlay.plot import PlotStyle
        from trdrop.compositor.overlay.text import TextStyle
        from trdrop.compositor.simple import SimpleCompositor
        from trdrop.engine import StreamingEngine
        from trdrop.export import StreamingCSVExporter, StreamingVideoExporter
        from trdrop.profiling.profiler import reset_profiler as do_reset
        from trdrop.source.sequential import SequentialFrameSource
        from trdrop.video.reader import PyAVReader

        # Reset profiler and optionally enable
        do_reset()
        if profile_path:
            os.environ["TRDROP_PROFILE"] = str(profile_path)

        # Create test videos
        video_paths = self._create_test_videos(tmp_path, config)

        # Create readers and sources
        readers = [PyAVReader(path) for path in video_paths]
        sources = [SequentialFrameSource(reader) for reader in readers]

        # Output dimensions - keep same as input for fair comparison
        output_width = config.width
        output_height = config.height

        # Create overlay styles
        plot_font = QFont("Helvetica Neue", 10)
        title_font = QFont("Helvetica Neue", 12)
        text_font = QFont("Helvetica Neue", 16)

        plot_style = PlotStyle(
            line_color=QColor(255, 100, 200),
            background_color=QColor(0, 0, 0, 120),
            axis_color=QColor(236, 236, 236),
            grid_color=QColor(255, 255, 255, 60),
            text_color=QColor(255, 255, 255),
            shadow_color=QColor(0, 0, 0),
            font=plot_font,
            title_font=title_font,
            line_width=2,
            shadow_offset=2,
            show_grid=True,
            show_labels=True,
        )

        text_style = TextStyle(
            color=QColor(255, 255, 255),
            shadow_color=QColor(0, 0, 0),
            font=text_font,
            shadow_offset=2,
        )

        # Create overlays for each video
        fps_texts = [FPSText(text_style, prefix="FPS:") for _ in range(config.video_count)]
        framerate_plots = [
            FrameratePlot(plot_style, max_fps=float(config.container_fps))
            for _ in range(config.video_count)
        ]

        # Create compositor
        compositor = SimpleCompositor(
            video_count=config.video_count,
            video_fps=[float(readers[i].fps) for i in range(config.video_count)],
            output_width=output_width,
            output_height=output_height,
            fps_texts=fps_texts,
            framerate_plots=framerate_plots,
        )

        # Create exporters
        output_video = tmp_path / "output.mp4"
        output_csv = tmp_path / "metrics.csv"

        video_exporter = StreamingVideoExporter(
            output_video,
            fps=readers[0].fps,
            codec="libx264",
            crf=23,
            preset="ultrafast",
        )
        csv_exporter = StreamingCSVExporter(output_csv)

        # Create engine
        engine = StreamingEngine(
            sources=sources,
            analyzers=[DuplicateDetector()],
            compositor=compositor,
            exporters=[video_exporter, csv_exporter],
            synchronous=synchronous,
        )

        # Run pipeline
        import time

        start_time = time.perf_counter()
        engine.run()
        total_time = time.perf_counter() - start_time

        # Calculate results
        total_frames = int(config.container_fps * config.duration_sec) - 1
        fps = total_frames / total_time

        results = {
            "config_name": config.name,
            "video_count": config.video_count,
            "total_frames": total_frames,
            "total_time_sec": total_time,
            "fps": fps,
            "frame_time_ms": (total_time / total_frames) * 1000,
        }

        # Read profile data if available
        if profile_path and profile_path.exists():
            with open(profile_path) as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if rows:
                # Calculate averages from profile
                read_times = [float(r.get("read_total_ms", 0)) for r in rows]
                analysis_times = [float(r.get("analysis_total_ms", 0)) for r in rows]
                compositor_times = [float(r.get("compositor_total_ms", 0)) for r in rows]
                export_times = [float(r.get("export_video_total_ms", 0)) for r in rows]

                results["avg_read_ms"] = np.mean(read_times)
                results["avg_analysis_ms"] = np.mean(analysis_times)
                results["avg_compositor_ms"] = np.mean(compositor_times)
                results["avg_export_ms"] = np.mean(export_times)

        return results

    @pytest.mark.parametrize(
        "config",
        BENCHMARK_CONFIGS,
        ids=[c.name for c in BENCHMARK_CONFIGS],
    )
    def test_benchmark(
        self,
        qapp,
        reset_profiler,
        tmp_path: Path,
        config: BenchmarkConfig,
    ) -> None:
        """Run benchmark for a specific configuration."""
        profile_path = tmp_path / f"profile_{config.name}.csv"

        print(f"\n\nBenchmark: {config.name}")
        print(f"  Videos: {config.video_count}")
        print(f"  Resolution: {config.width}x{config.height}")
        print(
            f"  Duration: {config.duration_sec}s @ "
            f"{config.container_fps}fps container / {config.content_fps}fps content"
        )

        results = self._run_benchmark(qapp, tmp_path, config, profile_path)

        print("\nResults:")
        print(f"  Total time: {results['total_time_sec']:.2f}s")
        print(f"  Throughput: {results['fps']:.1f} fps")
        print(f"  Frame time: {results['frame_time_ms']:.1f} ms")

        if "avg_read_ms" in results:
            print("\nPer-stage breakdown (avg ms/frame):")
            print(f"  Read:       {results['avg_read_ms']:.2f} ms")
            print(f"  Analysis:   {results['avg_analysis_ms']:.2f} ms")
            print(f"  Compositor: {results['avg_compositor_ms']:.2f} ms")
            print(f"  Export:     {results['avg_export_ms']:.2f} ms")

        # Basic sanity checks
        assert results["total_frames"] > 0
        assert results["fps"] > 0

    def test_multi_video_layout_correctness(
        self,
        qapp,
        reset_profiler,
        tmp_path: Path,
    ) -> None:
        """Verify that multi-video layout renders correctly."""
        from trdrop.compositor.simple import SimpleCompositor
        from trdrop.types.frames import FramePair, FrameView
        from trdrop.types.metrics import FrameMetrics

        # Create compositor for 4 videos
        video_count = 4
        output_width = 1280
        output_height = 720

        compositor = SimpleCompositor(
            video_count=video_count,
            video_fps=[60.0] * video_count,
            output_width=output_width,
            output_height=output_height,
        )

        # Create dummy frames with distinct colors for each video
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
        ]

        frame_height = output_height
        frame_width = output_width  # Each source video is full resolution

        pairs = []
        results = []

        for i in range(video_count):
            # Create solid color frame
            frame_data = np.full((frame_height, frame_width, 3), colors[i], dtype=np.uint8)
            view = FrameView(_data=frame_data, index=0, pts=0)
            pair = FramePair(prev=view, curr=view, _on_release=lambda: None)
            pairs.append(pair)
            results.append(FrameMetrics(frame_index=0, is_duplicate=False, diff_ratio=0.0))

        # Process frame
        output = compositor.process(pairs, results)

        # Verify output dimensions
        assert output.frame.shape == (output_height, output_width, 3)

        # Verify each video region has the correct color
        video_width = output_width // video_count

        for i, color in enumerate(colors):
            x_start = i * video_width
            x_mid = x_start + video_width // 2

            # Sample center of each video region
            sample = output.frame[output_height // 2, x_mid, :]

            # Check color matches (allowing some tolerance for encoding artifacts)
            np.testing.assert_allclose(
                sample,
                color,
                atol=5,
                err_msg=f"Video {i} region should be {color}, got {sample}",
            )

        print("\n\nMulti-video layout verification passed:")
        print(f"  Output: {output_width}x{output_height}")
        print(f"  Videos: {video_count}")
        print(f"  Per-video width: {video_width}px")
        for i, color in enumerate(colors):
            print(f"  Video {i}: RGB{color}")


class TestBenchmarkComparison:
    """Tests for comparing benchmark results over time."""

    @pytest.fixture(scope="class")
    def qapp(self):
        """Create QGuiApplication for font rendering."""
        app = QGuiApplication.instance()
        if app is None:
            app = QGuiApplication(sys.argv)
        return app

    @pytest.fixture
    def reset_profiler(self):
        """Reset the profiler singleton after each test."""
        from trdrop.profiling.profiler import reset_profiler

        yield
        reset_profiler()
        if "TRDROP_PROFILE" in os.environ:
            del os.environ["TRDROP_PROFILE"]

    def test_scaling_analysis(
        self,
        qapp,
        reset_profiler,
        tmp_path: Path,
    ) -> None:
        """Analyze how performance scales with video count."""
        from trdrop.profiling.profiler import reset_profiler as do_reset

        results = []

        for config in BENCHMARK_CONFIGS:
            do_reset()
            if "TRDROP_PROFILE" in os.environ:
                del os.environ["TRDROP_PROFILE"]

            profile_path = tmp_path / f"profile_{config.name}.csv"
            os.environ["TRDROP_PROFILE"] = str(profile_path)

            benchmark = TestBenchmarks()
            result = benchmark._run_benchmark(qapp, tmp_path / config.name, config, profile_path)
            results.append(result)

        print("\n\n" + "=" * 60)
        print("SCALING ANALYSIS")
        print("=" * 60)

        # Print comparison table
        print(f"\n{'Videos':<8} {'FPS':<10} {'Frame (ms)':<12} {'Compositor (ms)':<16}")
        print("-" * 50)

        baseline_fps = results[0]["fps"] if results else 1.0

        for r in results:
            comp_ms = r.get("avg_compositor_ms", 0)
            scaling = r["fps"] / baseline_fps if baseline_fps > 0 else 0
            print(
                f"{r['video_count']:<8} {r['fps']:<10.1f} {r['frame_time_ms']:<12.1f} "
                f"{comp_ms:<16.2f}"
            )

        print("\nScaling factor (relative to single video):")
        for r in results:
            scaling = baseline_fps / r["fps"] if r["fps"] > 0 else float("inf")
            print(f"  {r['video_count']} videos: {scaling:.2f}x slowdown")

        # Verify reasonable scaling - shouldn't be worse than O(n^2)
        if len(results) >= 2:
            single_fps = results[0]["fps"]
            quad_fps = results[-1]["fps"]
            slowdown = single_fps / quad_fps if quad_fps > 0 else float("inf")

            # With 4 videos, expect at most ~4-8x slowdown (not 16x = O(n^2))
            assert slowdown < 16, (
                f"Scaling worse than O(n^2): {slowdown:.1f}x slowdown for 4 videos"
            )

    def test_memory_constant_after_warmup(
        self,
        qapp,
        reset_profiler,
        tmp_path: Path,
    ) -> None:
        """Verify O(1) memory: no growth after processing first frames.

        Creates 4 videos and processes them, measuring memory after frame 2
        and after frame 50. Memory should not grow significantly.
        """
        import tracemalloc

        from trdrop.analysis.duplicate import DuplicateDetector
        from trdrop.compositor.simple import SimpleCompositor
        from trdrop.source.sequential import SequentialFrameSource
        from trdrop.video.reader import PyAVReader

        # Create 4 test videos (short duration for speed)
        config = BenchmarkConfig(
            name="memory_test",
            video_count=4,
            duration_sec=1.0,  # 60 frames
        )
        video_paths = []
        for i in range(config.video_count):
            video_path = tmp_path / f"mem_source_{i}.mp4"
            video_config = VideoConfig(
                container_fps=config.container_fps,
                content_fps=config.content_fps,
                duration_sec=config.duration_sec,
                width=config.width,
                height=config.height,
                pattern=config.pattern,
                seed=42 + i,
            )
            VideoGenerator(video_config).write(video_path)
            video_paths.append(video_path)

        # Set up pipeline components
        readers = [PyAVReader(path) for path in video_paths]
        sources = [SequentialFrameSource(reader) for reader in readers]
        source_iters = [iter(src) for src in sources]
        analyzer = DuplicateDetector()
        compositor = SimpleCompositor(
            video_count=config.video_count,
            video_fps=[float(r.fps) for r in readers],
            output_width=config.width,
            output_height=config.height,
        )

        # Start memory tracking
        tracemalloc.start()

        # Process first 2 frames (warmup)
        for frame_idx in range(2):
            pairs = [next(it, None) for it in source_iters]
            if any(p is None for p in pairs):
                break
            results = [analyzer.map(p) for p in pairs]
            compositor.process(pairs, results)
            for p in pairs:
                p.release()

        # Measure memory after warmup
        snapshot_after_warmup = tracemalloc.take_snapshot()
        mem_after_warmup = sum(stat.size for stat in snapshot_after_warmup.statistics("lineno"))

        # Process 50 more frames
        for frame_idx in range(50):
            pairs = [next(it, None) for it in source_iters]
            if any(p is None for p in pairs):
                break
            results = [analyzer.map(p) for p in pairs]
            compositor.process(pairs, results)
            for p in pairs:
                p.release()

        # Measure memory after processing
        snapshot_after_processing = tracemalloc.take_snapshot()
        mem_after_processing = sum(
            stat.size for stat in snapshot_after_processing.statistics("lineno")
        )

        tracemalloc.stop()

        # Calculate growth
        mem_growth = mem_after_processing - mem_after_warmup
        mem_growth_mb = mem_growth / (1024 * 1024)
        mem_growth_pct = (mem_growth / mem_after_warmup) * 100 if mem_after_warmup > 0 else 0

        print("\n\n" + "=" * 60)
        print("MEMORY ANALYSIS (4 videos, 1280x720)")
        print("=" * 60)
        print(f"\nMemory after warmup (2 frames):  {mem_after_warmup / 1024 / 1024:.1f} MB")
        print(f"Memory after 50 frames:          {mem_after_processing / 1024 / 1024:.1f} MB")
        print(f"Memory growth:                   {mem_growth_mb:+.2f} MB ({mem_growth_pct:+.1f}%)")

        # Allow up to 10% growth (for Python GC overhead, small allocations)
        # True O(1) would be 0%, but we allow some tolerance
        max_allowed_growth_pct = 10.0
        assert mem_growth_pct < max_allowed_growth_pct, (
            f"Memory grew by {mem_growth_pct:.1f}% after warmup, "
            f"expected <{max_allowed_growth_pct}% for O(1) memory"
        )

        print(f"\nResult: Memory growth {mem_growth_mb:+.3f} MB (target: O(1))")

    def test_sync_vs_async_export(
        self,
        qapp,
        reset_profiler,
        tmp_path: Path,
    ) -> None:
        """Compare synchronous vs asynchronous export performance.

        Measures pipeline overlap achieved by async export.
        """
        from trdrop.profiling.profiler import reset_profiler as do_reset

        # Use single video config with longer duration for more accurate measurement
        config = BenchmarkConfig(
            name="async_test",
            video_count=1,
            duration_sec=3.0,  # 180 frames
        )

        # Run synchronous
        do_reset()
        if "TRDROP_PROFILE" in os.environ:
            del os.environ["TRDROP_PROFILE"]
        sync_profile = tmp_path / "sync_profile.csv"
        os.environ["TRDROP_PROFILE"] = str(sync_profile)

        benchmark = TestBenchmarks()
        sync_result = benchmark._run_benchmark(
            qapp, tmp_path / "sync", config, sync_profile, synchronous=True
        )

        # Run asynchronous
        do_reset()
        if "TRDROP_PROFILE" in os.environ:
            del os.environ["TRDROP_PROFILE"]
        async_profile = tmp_path / "async_profile.csv"
        os.environ["TRDROP_PROFILE"] = str(async_profile)

        async_result = benchmark._run_benchmark(
            qapp, tmp_path / "async", config, async_profile, synchronous=False
        )

        print("\n\n" + "=" * 60)
        print("SYNC vs ASYNC EXPORT COMPARISON")
        print("=" * 60)
        print(f"\nConfiguration: {config.video_count} video, {config.duration_sec}s")
        print(f"Total frames: {sync_result['total_frames']}")

        print(f"\n{'Mode':<12} {'Total (s)':<12} {'FPS':<10} {'Frame (ms)':<12}")
        print("-" * 50)
        print(
            f"{'Sync':<12} {sync_result['total_time_sec']:<12.2f} "
            f"{sync_result['fps']:<10.1f} {sync_result['frame_time_ms']:<12.2f}"
        )
        print(
            f"{'Async':<12} {async_result['total_time_sec']:<12.2f} "
            f"{async_result['fps']:<10.1f} {async_result['frame_time_ms']:<12.2f}"
        )

        # Calculate speedup
        speedup = sync_result['total_time_sec'] / async_result['total_time_sec']
        time_saved = sync_result['total_time_sec'] - async_result['total_time_sec']
        time_saved_per_frame = (time_saved / sync_result['total_frames']) * 1000

        print(f"\nAsync speedup: {speedup:.3f}x")
        print(f"Time saved: {time_saved:.3f}s total, {time_saved_per_frame:.2f}ms/frame")

        # Per-stage comparison
        if "avg_export_ms" in sync_result and "avg_export_ms" in async_result:
            print(f"\nPer-stage breakdown:")
            print(f"  Sync export:  {sync_result.get('avg_export_ms', 0):.2f} ms/frame")
            print(f"  Async export: {async_result.get('avg_export_ms', 0):.2f} ms/frame")

            # Calculate theoretical overlap
            export_ms = sync_result.get('avg_export_ms', 0)
            read_ms = sync_result.get('avg_read_ms', 0)
            analysis_ms = sync_result.get('avg_analysis_ms', 0)
            overlap_potential = min(export_ms, read_ms + analysis_ms)
            print(f"\n  Export time: {export_ms:.2f} ms")
            print(f"  Read+Analysis time: {read_ms + analysis_ms:.2f} ms")
            print(f"  Max overlap potential: {overlap_potential:.2f} ms/frame")
            print(f"  Actual overlap: {time_saved_per_frame:.2f} ms/frame")

        # Async should be faster (or at least not slower)
        assert async_result['total_time_sec'] <= sync_result['total_time_sec'] * 1.05, (
            f"Async should not be significantly slower than sync"
        )
