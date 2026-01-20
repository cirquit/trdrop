"""Demo: Generate and process a video with overlays."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtGui import QColor, QFont, QGuiApplication

# Must create QGuiApplication before using fonts
app = QGuiApplication(sys.argv)

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.compositor.overlay import (
    FrameratePlot,
    FrametimePlot,
    FPSText,
    PlotStyle,
    get_video_color,
)
from trdrop.compositor.overlay.text import TextStyle
from trdrop.compositor.simple import SimpleCompositor
from trdrop.engine import StreamingEngine
from trdrop.export import StreamingCSVExporter, StreamingVideoExporter
from trdrop.source.sequential import SequentialFrameSource
from trdrop.video.reader import PyAVReader


def print_progress(current: int, total: int, width: int = 40) -> None:
    """Print a portable progress bar that overwrites itself."""
    pct = current / total
    filled = int(width * pct)
    bar = "=" * filled + ">" + " " * (width - filled - 1) if filled < width else "=" * width
    sys.stdout.write(f"\r  [{bar}] {current}/{total} ({pct * 100:.1f}%)")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")


def main() -> None:
    output_dir = Path(__file__).parent
    source_video = output_dir / "demo_source.mp4"
    output_video = output_dir / "demo_output.mp4"
    output_csv = output_dir / "demo_metrics.csv"

    # Generate 5-second test video: 30fps content in 60fps container
    print("Generating 5-second test video (30fps in 60fps container)...")
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

    # Create overlay styles
    title_font = QFont("Arial", 16)
    title_font.setWeight(QFont.Weight.Bold)

    plot_style = PlotStyle(
        line_color=get_video_color(0),
        background_color=QColor(0, 0, 0, 180),
        axis_color=QColor(236, 236, 236),
        grid_color=QColor(255, 255, 255, 100),
        text_color=QColor(255, 255, 255),
        shadow_color=QColor(0, 0, 0),
        font=QFont("Arial", 12),
        title_font=title_font,
        line_width=2,
        show_grid=True,
        show_labels=True,
    )

    fps_font = QFont("Arial", 28)
    fps_font.setWeight(QFont.Weight.Bold)

    text_style = TextStyle(
        color=get_video_color(0),
        shadow_color=QColor(0, 0, 0),
        font=fps_font,
        shadow_offset=2,
    )

    # Create overlay elements
    fps_text = FPSText(text_style, prefix="FPS:")
    framerate_plot = FrameratePlot(
        plot_style,
        max_fps=60.0,
        show_center_line=True,
        auto_scale=True,
        time_anchor=0.5,
        show_time_indicator=True,
        show_start_marker=True,
    )
    frametime_plot = FrametimePlot(
        plot_style,
        max_ms=50.0,
        auto_scale=True,
        show_current_value=True,
        time_anchor=1.0,  # Frametime plot stays at right edge
        show_time_indicator=False,  # No indicator for frametime
        show_start_marker=False,
    )

    # Create compositor with overlays
    compositor = SimpleCompositor(
        video_count=1,
        video_fps=[reader.fps],
        output_width=1280,
        output_height=720,
        fps_texts=[fps_text],
        framerate_plots=[framerate_plot],
        frametime_plots=[frametime_plot],
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
    print("Processing with overlays...")

    engine = StreamingEngine(
        sources=[source],
        analyzers=[DuplicateDetector()],
        compositor=compositor,
        exporters=[video_exporter, csv_exporter],
        on_frame=lambda idx, total: print_progress(idx + 1, total),
    )

    engine.run()

    print("Done!")
    print(f"  Output video: {output_video}")
    print(f"  Output CSV: {output_csv}")
    print(f"  Video size: {output_video.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
