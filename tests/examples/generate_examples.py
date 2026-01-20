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
from trdrop.compositor.overlay import FPSText, FrameratePlot  # noqa: E402
from trdrop.compositor.overlay.plot import PlotStyle  # noqa: E402
from trdrop.compositor.overlay.text import TextStyle  # noqa: E402
from trdrop.engine import StreamingEngine  # noqa: E402
from trdrop.export import StreamingVideoExporter  # noqa: E402
from trdrop.source.sequential import SequentialFrameSource  # noqa: E402
from trdrop.video.reader import PyAVReader  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "examples" / "generated"

EXAMPLES = [
    {"name": "single_crop", "video_count": 1, "scale_mode": ScaleMode.CROP},
    {"name": "single_fit", "video_count": 1, "scale_mode": ScaleMode.FIT},
    {"name": "single_stretch", "video_count": 1, "scale_mode": ScaleMode.STRETCH},
    {"name": "dual_crop", "video_count": 2, "scale_mode": ScaleMode.CROP},
    {"name": "triple_crop", "video_count": 3, "scale_mode": ScaleMode.CROP},
    {"name": "quad_crop", "video_count": 4, "scale_mode": ScaleMode.CROP},
    {"name": "dual_fit", "video_count": 2, "scale_mode": ScaleMode.FIT},
    {"name": "quad_fit", "video_count": 4, "scale_mode": ScaleMode.FIT},
]


def create_styles():
    """Create overlay styles."""
    plot_style = PlotStyle(
        line_color=QColor(255, 100, 200),
        background_color=QColor(0, 0, 0, 120),
        axis_color=QColor(236, 236, 236),
        grid_color=QColor(255, 255, 255, 60),
        text_color=QColor(255, 255, 255),
        shadow_color=QColor(0, 0, 0),
        font=QFont("Helvetica Neue", 10),
        title_font=QFont("Helvetica Neue", 12),
        line_width=2,
        shadow_offset=2,
        show_grid=True,
        show_labels=True,
    )
    text_style = TextStyle(
        color=QColor(255, 255, 255),
        shadow_color=QColor(0, 0, 0),
        font=QFont("Helvetica Neue", 18),
        shadow_offset=2,
    )
    return plot_style, text_style


def generate_sources(output_dir: Path, count: int = 4) -> list[Path]:
    """Generate source test videos."""
    print("Creating source videos...")
    paths = []
    for i in range(count):
        path = output_dir / f"source_{i}.mp4"
        VideoConfig(
            container_fps=60,
            content_fps=[30, 24, 45, 30][i % 4],
            duration_sec=3.0,
            width=1280,
            height=720,
            pattern=PatternType.NUMBER,
            seed=42 + i * 100,
        ).resolve()
        VideoGenerator(VideoConfig(
            container_fps=60,
            content_fps=[30, 24, 45, 30][i % 4],
            duration_sec=3.0,
            width=1280,
            height=720,
            pattern=PatternType.NUMBER,
            seed=42 + i * 100,
        )).write(path)
        print(f"  {path.name}")
        paths.append(path)
    return paths


def generate_example(cfg: dict, sources: list[Path]) -> Path:
    """Generate one example."""
    name = cfg["name"]
    n = cfg["video_count"]
    mode = cfg["scale_mode"]

    print(f"\n{name}: {n} video(s), {mode.name}")

    readers = [PyAVReader(p) for p in sources[:n]]
    plot_style, text_style = create_styles()

    compositor = SimpleCompositor(
        video_count=n,
        video_fps=[float(r.fps) for r in readers],
        output_width=1280,
        output_height=720,
        scale_mode=mode,
        fps_texts=[FPSText(text_style, prefix="FPS:") for _ in range(n)],
        framerate_plots=[FrameratePlot(plot_style, max_fps=60.0) for _ in range(n)],
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
