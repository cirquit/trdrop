"""Test profiling functionality."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import pytest


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


@pytest.fixture
def temp_profile_path(tmp_path: Path) -> Path:
    """Create a temporary path for the profile output."""
    return tmp_path / "test_profile.csv"


@pytest.fixture
def reset_profiler():
    """Reset the profiler singleton after each test."""
    from trdrop.profiling.profiler import reset_profiler
    yield
    reset_profiler()
    # Also clean up environment
    if "TRDROP_PROFILE" in os.environ:
        del os.environ["TRDROP_PROFILE"]


class TestProfiler:
    """Test profiler core functionality."""

    def test_null_profiler_when_env_not_set(self, reset_profiler) -> None:
        """NullProfiler returned when TRDROP_PROFILE not set."""
        from trdrop.profiling.profiler import NullProfiler, get_profiler, reset_profiler

        reset_profiler()
        if "TRDROP_PROFILE" in os.environ:
            del os.environ["TRDROP_PROFILE"]

        profiler = get_profiler()
        assert isinstance(profiler, NullProfiler)
        assert not profiler.enabled

    def test_profiler_when_env_set(self, reset_profiler, temp_profile_path: Path) -> None:
        """Profiler returned when TRDROP_PROFILE is set."""
        from trdrop.profiling.profiler import Profiler, get_profiler, reset_profiler

        reset_profiler()
        os.environ["TRDROP_PROFILE"] = str(temp_profile_path)

        profiler = get_profiler()
        assert isinstance(profiler, Profiler)
        assert profiler.enabled
        assert profiler.output_path == temp_profile_path

    def test_frame_timing_collection(self, reset_profiler, temp_profile_path: Path) -> None:
        """Test that frame timings are collected correctly."""
        from trdrop.profiling.profiler import Profiler

        profiler = Profiler(temp_profile_path)

        profiler.start_run()

        # Simulate 3 frames
        for i in range(3):
            profiler.start_frame(i)

            with profiler.time("read_total"):
                pass  # Simulate read

            with profiler.time("analysis_total"):
                pass  # Simulate analysis

            profiler.add_timing("compositor_total", 1.5)

            profiler.end_frame()

        profiler.end_run()

        # Check CSV was created
        assert temp_profile_path.exists()

        # Read and verify CSV
        with open(temp_profile_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        assert all(float(r["compositor_total_ms"]) == 1.5 for r in rows)

        # Check summary was created
        summary_path = temp_profile_path.with_suffix(".summary.txt")
        assert summary_path.exists()

        summary_content = summary_path.read_text()
        assert "Total frames: 3" in summary_content
        assert "Per-Stage Timing" in summary_content

    def test_null_profiler_is_noop(self, reset_profiler) -> None:
        """NullProfiler operations are no-ops."""
        from trdrop.profiling.profiler import NullProfiler

        profiler = NullProfiler()

        # These should not raise
        profiler.start_run()
        profiler.start_frame(0)

        with profiler.time("test_stage"):
            pass

        profiler.add_timing("test", 1.0)
        profiler.end_frame()
        profiler.end_run()


class TestProfilingIntegration:
    """Integration tests for profiling with the full pipeline."""

    @pytest.fixture(scope="class")
    def qapp(self):
        """Create QGuiApplication for font rendering."""
        from PyQt6.QtGui import QGuiApplication
        app = QGuiApplication.instance()
        if app is None:
            app = QGuiApplication(sys.argv)
        return app

    def test_pipeline_profiling(
        self,
        qapp,
        reset_profiler,
        temp_profile_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test profiling of the full pipeline."""
        from PyQt6.QtGui import QColor, QFont

        from tests.testkit import PatternType, VideoConfig, VideoGenerator
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

        # Reset to ensure clean state
        do_reset()
        os.environ["TRDROP_PROFILE"] = str(temp_profile_path)

        # Create short test video
        source_video = tmp_path / "source.mp4"
        output_video = tmp_path / "output.mp4"
        output_csv = tmp_path / "metrics.csv"

        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=0.5,  # Short video
            width=320,
            height=240,
            pattern=PatternType.SOLID,
        )
        VideoGenerator(config).write(source_video)

        # Setup reader and source
        reader = PyAVReader(source_video)
        source = SequentialFrameSource(reader)

        # Create overlay styles
        plot_font = QFont("Helvetica Neue", 10)
        title_font = QFont("Helvetica Neue", 12)

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

        text_font = QFont("Helvetica Neue", 16)
        text_style = TextStyle(
            color=QColor(255, 255, 255),
            shadow_color=QColor(0, 0, 0),
            font=text_font,
            shadow_offset=2,
        )

        fps_text = FPSText(text_style, prefix="FPS:")
        framerate_plot = FrameratePlot(plot_style, max_fps=60.0)

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=320,
            output_height=240,
            fps_texts=[fps_text],
            framerate_plots=[framerate_plot],
        )

        video_exporter = StreamingVideoExporter(
            output_video,
            fps=reader.fps,
            codec="libx264",
            crf=23,
            preset="ultrafast",
        )
        csv_exporter = StreamingCSVExporter(output_csv)

        engine = StreamingEngine(
            sources=[source],
            analyzers=[DuplicateDetector()],
            compositor=compositor,
            exporters=[video_exporter, csv_exporter],
            synchronous=True,
        )

        print("\nRunning pipeline with profiling enabled...")
        engine.run()

        # Verify profile was created
        assert temp_profile_path.exists(), "Profile CSV should be created"

        # Read and analyze profile
        with open(temp_profile_path) as f:
            reader_csv = csv.DictReader(f)
            rows = list(reader_csv)

        print(f"\n  Profiled {len(rows)} frames")

        # Should have profiled some frames
        assert len(rows) > 0, "Should have profiled at least one frame"

        # Check that key timings are present and positive
        first_row = rows[0]
        assert "frame_index" in first_row
        assert "read_total_ms" in first_row
        assert "analysis_total_ms" in first_row
        assert "compositor_total_ms" in first_row
        assert "export_video_total_ms" in first_row

        # Check summary file
        summary_path = temp_profile_path.with_suffix(".summary.txt")
        assert summary_path.exists(), "Summary file should be created"

        summary = summary_path.read_text()
        print(f"\nProfile Summary:\n{summary}")

        assert "Total frames:" in summary
        assert "Average FPS:" in summary
        assert "Time Distribution" in summary
        assert "Optimization Opportunities:" in summary
