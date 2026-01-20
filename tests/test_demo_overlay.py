"""Demo test: Generate a video with overlays for visual inspection."""

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


from tests.testkit import PatternType, VideoConfig, VideoGenerator  # noqa: E402
from trdrop.analysis.duplicate import DuplicateDetector  # noqa: E402
from trdrop.compositor.overlay import FPSText, FrameratePlot  # noqa: E402
from trdrop.compositor.overlay.plot import PlotStyle  # noqa: E402
from trdrop.compositor.overlay.text import TextStyle  # noqa: E402
from trdrop.compositor.simple import SimpleCompositor  # noqa: E402
from trdrop.engine import StreamingEngine  # noqa: E402
from trdrop.export import StreamingCSVExporter, StreamingVideoExporter  # noqa: E402
from trdrop.source.sequential import SequentialFrameSource  # noqa: E402
from trdrop.video.reader import PyAVReader  # noqa: E402


@pytest.fixture(scope="module")
def qapp() -> QGuiApplication:
    """Create QGuiApplication for font rendering."""
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app  # type: ignore[return-value]


class TestDemoOverlay:
    """Generate demo video for visual inspection."""

    def test_generate_5sec_overlay_video(self, qapp: QGuiApplication) -> None:
        """Generate a 5-second video with FPS overlay and plot."""
        output_dir = Path(__file__).parent.parent / "examples"
        output_dir.mkdir(exist_ok=True)

        source_video = output_dir / "demo_source.mp4"
        output_video = output_dir / "demo_output.mp4"
        output_csv = output_dir / "demo_metrics.csv"

        # Generate 5-second test video: 30fps content in 60fps container
        print("\nGenerating 5-second test video (30fps in 60fps container)...")
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=5.0,
            width=1280,
            height=720,
            pattern=PatternType.NUMBER,
        )
        VideoGenerator(config).write(source_video)
        print(f"  Source: {source_video}")

        # Setup reader and source
        reader = PyAVReader(source_video)
        source = SequentialFrameSource(reader)
        print(f"  Frames: {reader.total_frames}, FPS: {reader.fps}")

        # Create overlay styles (v1-inspired)
        # Try fonts: "Helvetica Neue", "Segoe UI", "SF Pro Display", "Arial"
        plot_font = QFont("Helvetica Neue", 14)
        plot_font.setWeight(QFont.Weight.Medium)

        title_font = QFont("Helvetica Neue", 18)
        title_font.setWeight(QFont.Weight.Bold)

        plot_style = PlotStyle(
            line_color=QColor(255, 100, 200),  # Pink like v1
            background_color=QColor(0, 0, 0, 120),  # More transparent to see video
            axis_color=QColor(236, 236, 236),  # Almost white
            grid_color=QColor(255, 255, 255, 60),  # Subtle grid
            text_color=QColor(255, 255, 255),
            shadow_color=QColor(0, 0, 0),  # Black shadow for contrast
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
            shadow_color=QColor(0, 0, 0),  # Black shadow
            font=text_font,
            shadow_offset=3,
        )

        # Create overlay elements
        fps_text = FPSText(text_style, prefix="FPS:")
        framerate_plot = FrameratePlot(plot_style, max_fps=60.0, show_center_line=True)

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
            crf=18,
            preset="medium",
        )
        csv_exporter = StreamingCSVExporter(output_csv)

        # Process
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

        out_reader = PyAVReader(output_video)
        assert out_reader.total_frames > 200  # Should have ~299 frames
        assert out_reader.width == 1280
        assert out_reader.height == 720
        out_reader.close()
