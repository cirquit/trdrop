"""Test varying FPS detection and plot auto-scaling."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PyQt6.QtGui import QColor, QFont, QGuiApplication


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


def generate_varying_fps_pattern(
    container_fps: int,
    segments: list[tuple[float, float]],
) -> list[int]:
    """Generate frame_pattern for varying FPS segments.

    Args:
        container_fps: Container framerate
        segments: List of (duration_sec, content_fps) tuples

    Returns:
        List of content indices for each frame
    """
    pattern: list[int] = []
    content_index = 0

    for duration_sec, content_fps in segments:
        frames_in_segment = int(container_fps * duration_sec)
        frames_per_content = container_fps / content_fps

        for i in range(frames_in_segment):
            # Calculate content index within this segment
            segment_content_idx = int(i / frames_per_content)
            pattern.append(content_index + segment_content_idx)

        # Advance content index for next segment
        unique_in_segment = int(content_fps * duration_sec)
        content_index += unique_in_segment

    return pattern


@pytest.fixture(scope="module")
def qapp() -> QGuiApplication:
    """Create QGuiApplication for font rendering."""
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app  # type: ignore[return-value]


class TestVaryingFPS:
    """Test varying FPS detection with auto-scaling plot."""

    def test_varying_fps_30_60_120(self, qapp: QGuiApplication) -> None:
        """Test FPS detection with varying content framerate: 30→60→120."""
        from tests.testkit import PatternType, VideoConfig, VideoGenerator
        from trdrop.analysis.duplicate import DuplicateDetector
        from trdrop.compositor.overlay import FPSText, FrameratePlot
        from trdrop.compositor.overlay.plot import PlotStyle
        from trdrop.compositor.overlay.text import TextStyle
        from trdrop.compositor.simple import SimpleCompositor
        from trdrop.engine import StreamingEngine
        from trdrop.export import StreamingCSVExporter, StreamingVideoExporter
        from trdrop.source.sequential import SequentialFrameSource
        from trdrop.video.reader import PyAVReader

        output_dir = Path(__file__).parent.parent / "examples"
        output_dir.mkdir(exist_ok=True)

        source_video = output_dir / "varying_fps_source.mp4"
        output_video = output_dir / "varying_fps_output.mp4"
        output_csv = output_dir / "varying_fps_metrics.csv"

        # 120fps container (faster than 600fps)
        container_fps = 120

        # Segments: (duration_sec, content_fps) - shorter duration
        # 0.5 second each: 30 → 60 → 120
        segments = [
            (0.5, 30.0),
            (0.5, 60.0),
            (0.5, 120.0),
        ]

        frame_pattern = generate_varying_fps_pattern(container_fps, segments)
        total_duration = sum(d for d, _ in segments)

        print(f"\nGenerating {total_duration}s test video at {container_fps}fps container...")
        print("  Segments: 30→60→120 fps")
        print(f"  Total frames: {len(frame_pattern)}")

        config = VideoConfig(
            container_fps=container_fps,
            content_fps=120,  # Max content FPS in segments
            duration_sec=total_duration,
            width=1280,
            height=720,
            pattern=PatternType.NUMBER,
            frame_pattern=frame_pattern,
        )
        VideoGenerator(config).write(source_video)
        print(f"  Source: {source_video}")

        # Setup reader and source
        reader = PyAVReader(source_video)
        source = SequentialFrameSource(reader)
        print(f"  Frames: {reader.total_frames}, Container FPS: {reader.fps}")

        # Create overlay styles
        plot_font = QFont("Helvetica Neue", 14)
        plot_font.setWeight(QFont.Weight.Medium)

        title_font = QFont("Helvetica Neue", 18)
        title_font.setWeight(QFont.Weight.Bold)

        plot_style = PlotStyle(
            line_color=QColor(255, 100, 200),
            background_color=QColor(0, 0, 0, 120),  # More transparent
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

        text_font = QFont("Helvetica Neue", 24)
        text_font.setWeight(QFont.Weight.Bold)

        text_style = TextStyle(
            color=QColor(255, 255, 255),
            shadow_color=QColor(0, 0, 0),
            font=text_font,
            shadow_offset=3,
        )

        # Create overlay elements with auto-scaling
        fps_text = FPSText(text_style, prefix="FPS:")
        framerate_plot = FrameratePlot(
            plot_style,
            max_fps=60.0,  # Minimum scale
            show_center_line=False,  # Disable center line for varying FPS
            auto_scale=True,  # Enable auto-scaling
        )

        # Create compositor with overlays
        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=1280,
            output_height=720,
            fps_texts=[fps_text],
            framerate_plots=[framerate_plot],
        )

        # Create exporters
        video_exporter = StreamingVideoExporter(
            output_video,
            fps=reader.fps,
            codec="libx264",
            crf=23,
            preset="ultrafast",
        )
        csv_exporter = StreamingCSVExporter(output_csv)

        # Process
        print("Processing with auto-scaling plot...")
        engine = StreamingEngine(
            sources=[source],
            analyzers=[DuplicateDetector()],
            compositor=compositor,
            exporters=[video_exporter, csv_exporter],
            on_frame=lambda idx, total: print_progress(idx + 1, total),
            synchronous=True,
        )

        engine.run()

        print(f"  Output video: {output_video}")
        print(f"  Output CSV: {output_csv}")
        print(f"  Video size: {output_video.stat().st_size / 1024 / 1024:.1f} MB")

        # Verify output
        assert output_video.exists()
        assert output_csv.exists()

        # Check that we got the expected FPS transitions in CSV
        import csv

        with open(output_csv) as f:
            reader_csv = csv.DictReader(f)
            rows = list(reader_csv)

        # Check FPS at different points (after ramp-up in each segment)
        # 120fps container, 0.5s segments:
        # Frame 60 = end of 30fps segment (should be ~30)
        # Frame 120 = end of 60fps segment (should be ~60)
        # Frame 179 = end of 120fps segment (should be ~120)

        fps_at_60 = float(rows[59]["windowed_fps"])
        fps_at_120 = float(rows[119]["windowed_fps"])
        fps_at_end = float(rows[-1]["windowed_fps"])

        print("\n  FPS measurements:")
        print(f"    At frame 60 (30fps segment): {fps_at_60:.1f}")
        print(f"    At frame 120 (60fps segment): {fps_at_120:.1f}")
        print(f"    At end (120fps segment): {fps_at_end:.1f}")

        # With 0.5s segments in 120fps container, window is still ramping up
        # FPS values will be lower than target but should show relative ordering
        # 30fps segment: ~15 (half of 30 due to 0.5s window fill)
        # 60fps segment: ~45 (30fps carry-over + 30fps worth of 60fps)
        # 120fps segment: ~90 (mixed carry-over)
        assert fps_at_60 < fps_at_120, "60fps segment should show higher FPS than 30fps"
        assert fps_at_120 < fps_at_end, "120fps segment should show higher FPS than 60fps"
        # End should show highest FPS
        assert fps_at_end > 60, f"Final FPS should exceed 60, got {fps_at_end}"
