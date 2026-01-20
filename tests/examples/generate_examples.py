#!/usr/bin/env python3
"""Generate visual examples for manual confirmation.

Run via: make examples
Output: examples/generated/
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))  # Add project root for tests.testkit

from PyQt6.QtGui import QColor, QFont, QGuiApplication  # noqa: E402

from tests.testkit import PatternType, VideoConfig, VideoGenerator  # noqa: E402
from trdrop.analysis.duplicate import DuplicateDetector  # noqa: E402
from trdrop.compositor import ScaleMode, SimpleCompositor  # noqa: E402
from trdrop.compositor.overlay import FrameratePlot, FrametimePlot, FPSText  # noqa: E402
from trdrop.compositor.overlay.plot import PlotStyle  # noqa: E402
from trdrop.compositor.overlay.text import TextStyle  # noqa: E402
from trdrop.engine import StreamingEngine  # noqa: E402
from trdrop.export import StreamingVideoExporter  # noqa: E402
from trdrop.source.sequential import SequentialFrameSource  # noqa: E402
from trdrop.video.reader import PyAVReader  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "examples" / "generated"

# Source video configurations with different framerates for comparison
SOURCE_CONFIGS = [
    {"content_fps": 60, "label": "60fps"},    # Full framerate
    {"content_fps": 30, "label": "30fps"},    # Half framerate
    {"content_fps": 24, "label": "24fps"},    # Film framerate
    {"content_fps": 20, "label": "20fps"},    # Low framerate
]

# Example configurations - CROP mode only (FIT/STRETCH are optional)
EXAMPLES = [
    {"name": "single", "video_count": 1},
    {"name": "dual", "video_count": 2},
    {"name": "triple", "video_count": 3},
    {"name": "quad", "video_count": 4},
]


def create_styles():
    """Create overlay styles."""
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

    fps_font = QFont("Helvetica Neue", 18)
    fps_font.setWeight(QFont.Weight.Bold)

    text_style = TextStyle(
        color=QColor(255, 255, 255),
        shadow_color=QColor(0, 0, 0),
        font=fps_font,
        shadow_offset=2,
    )
    return plot_style, text_style


def generate_sources(output_dir: Path) -> list[Path]:
    """Generate source test videos with different framerates."""
    print("Creating source videos with varying framerates...")
    paths = []
    for i, cfg in enumerate(SOURCE_CONFIGS):
        path = output_dir / f"source_{cfg['label']}.mp4"
        video_config = VideoConfig(
            container_fps=60,
            content_fps=cfg["content_fps"],
            duration_sec=3.0,
            width=1280,
            height=720,
            pattern=PatternType.NUMBER,
            seed=42 + i * 100,
        )
        VideoGenerator(video_config).write(path)
        print(f"  {path.name} ({cfg['content_fps']}fps content in 60fps container)")
        paths.append(path)
    return paths


def generate_example(cfg: dict, sources: list[Path]) -> Path:
    """Generate one example with CROP mode."""
    name = cfg["name"]
    n = cfg["video_count"]

    print(f"\n{name}: {n} video(s)")

    readers = [PyAVReader(sources[i % len(sources)]) for i in range(n)]
    plot_style, text_style = create_styles()

    # Create overlays with centered time, indicators, and markers
    fps_texts = [FPSText(text_style, prefix="FPS:") for _ in range(n)]
    framerate_plots = [
        FrameratePlot(
            plot_style,
            max_fps=60.0,
            time_anchor=0.5,
            show_time_indicator=True,
            show_start_marker=True,
        )
        for _ in range(n)
    ]
    frametime_plots = [
        FrametimePlot(
            plot_style,
            max_ms=50.0,
            auto_scale=True,
            show_current_value=True,
            time_anchor=0.5,
            show_time_indicator=True,
            show_start_marker=True,
        )
        for _ in range(n)
    ]

    compositor = SimpleCompositor(
        video_count=n,
        video_fps=[float(r.fps) for r in readers],
        output_width=1920,
        output_height=1080,
        scale_mode=ScaleMode.CROP,
        fps_texts=fps_texts,
        framerate_plots=framerate_plots,
        frametime_plots=frametime_plots,
    )

    output_path = OUTPUT_DIR / f"{name}.mp4"
    engine = StreamingEngine(
        sources=[SequentialFrameSource(r) for r in readers],
        analyzers=[DuplicateDetector()],
        compositor=compositor,
        exporters=[StreamingVideoExporter(output_path, fps=readers[0].fps)],
        synchronous=True,
    )
    engine.run()
    print(f"  -> {output_path}")
    return output_path


def main():
    """Generate all examples."""
    print("=" * 50)
    print("TRDrop Visual Examples")
    print("=" * 50)

    _app = QGuiApplication.instance() or QGuiApplication(sys.argv)  # noqa: F841
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = generate_sources(OUTPUT_DIR)
    for cfg in EXAMPLES:
        generate_example(cfg, sources)

    print(f"\nDone. Check: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
