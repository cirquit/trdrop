"""Test overlay rendering correctness.

Tests that overlays are actually drawn and visible on output frames.
"""

from __future__ import annotations

import sys

import numpy as np
import pytest
from PyQt6.QtGui import QColor, QFont, QGuiApplication

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.compositor.overlay import FPSText, FrameratePlot, FrametimePlot, PlotStyle
from trdrop.compositor.overlay.text import TextStyle
from trdrop.compositor.simple import SimpleCompositor
from trdrop.source.sequential import SequentialFrameSource
from trdrop.video.reader import PyAVReader


@pytest.fixture(scope="module")
def qapp() -> QGuiApplication:
    """Create QGuiApplication for font rendering."""
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app  # type: ignore[return-value]


@pytest.fixture(scope="module")
def test_video(tmp_path_factory, qapp):  # type: ignore[misc]
    """Create a short test video for overlay tests."""
    tmp_path = tmp_path_factory.mktemp("overlay_test")
    video_path = tmp_path / "test.mp4"

    config = VideoConfig(
        container_fps=60,
        content_fps=30,
        duration_sec=1.0,
        width=1280,
        height=720,
        pattern=PatternType.NUMBER,
        seed=42,
    )
    VideoGenerator(config).write(video_path)

    reader = PyAVReader(video_path)
    yield reader
    reader.close()


@pytest.fixture
def plot_style(qapp) -> PlotStyle:
    """Create standard plot style."""
    return PlotStyle(
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


@pytest.fixture
def text_style(qapp) -> TextStyle:
    """Create standard text style."""
    return TextStyle(
        color=QColor(255, 255, 255),
        shadow_color=QColor(0, 0, 0),
        font=QFont("Helvetica Neue", 16),
        shadow_offset=2,
    )


class TestOverlayRendering:
    """Test that overlays are actually rendered."""

    def test_multi_video_plots_fit(self, qapp, tmp_path, plot_style, text_style):
        """Verify plots fit properly in multi-video layouts (2, 3, 4 videos)."""
        videos = []
        for i in range(4):
            video_path = tmp_path / f"test_{i}.mp4"
            config = VideoConfig(
                container_fps=60,
                content_fps=30,
                duration_sec=0.5,
                width=1280,
                height=720,
                pattern=PatternType.NUMBER,
                seed=42 + i,
            )
            VideoGenerator(config).write(video_path)
            videos.append(PyAVReader(video_path))

        analyzer = DuplicateDetector()

        for video_count in [2, 3, 4]:
            compositor = SimpleCompositor(
                video_count=video_count,
                video_fps=[v.fps for v in videos[:video_count]],
                output_width=1920,
                output_height=1080,
                fps_texts=[
                    FPSText(text_style, prefix="FPS:") for _ in range(video_count)
                ],
                framerate_plots=[
                    FrameratePlot(plot_style, max_fps=60.0) for _ in range(video_count)
                ],
                frametime_plots=[
                    FrametimePlot(plot_style, max_ms=50.0) for _ in range(video_count)
                ],
            )

            sources = [SequentialFrameSource(videos[i]) for i in range(video_count)]
            source_iters = [iter(s) for s in sources]

            output = None
            for _ in range(20):
                pairs = []
                all_done = False
                for it in source_iters:
                    pair = next(it, None)
                    if pair is None:
                        all_done = True
                        break
                    pairs.append(pair)

                if all_done:
                    for p in pairs:
                        p.release()
                    break

                results = [analyzer.map(p) for p in pairs]
                output = compositor.process(pairs, results)

                for p in pairs:
                    p.release()

            assert output is not None
            frame = output.frame
            height, width = frame.shape[:2]
            video_width = width // video_count

            for i in range(video_count):
                slot_x = i * video_width
                slot_region = frame[:, slot_x:slot_x + video_width]

                bottom_region = slot_region[int(height * 0.75):, :]
                bottom_bright = np.sum(bottom_region > 100)

                mid_y_start = int(height * 0.45)
                mid_y_end = int(height * 0.65)
                left_quarter = slot_region[mid_y_start:mid_y_end, :video_width // 3]
                left_bright = np.sum(left_quarter > 100)

                assert bottom_bright > 500, (
                    f"{video_count}-video layout: slot {i} framerate plot missing"
                )
                assert left_bright > 100, (
                    f"{video_count}-video layout: slot {i} frametime plot missing"
                )

            print(f"  {video_count}-video layout: all plots visible")

        for v in videos:
            v.close()

    def test_plot_region_has_content(self, qapp, test_video, plot_style, text_style):
        """Verify plot regions contain non-black pixels after rendering."""
        source = SequentialFrameSource(test_video)
        analyzer = DuplicateDetector()

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[test_video.fps],
            output_width=1280,
            output_height=720,
            framerate_plots=[FrameratePlot(plot_style, max_fps=60.0)],
            frametime_plots=[FrametimePlot(plot_style, max_ms=50.0)],
        )

        output = None
        for i, pair in enumerate(source):
            if i >= 30:
                pair.release()
                break
            result = analyzer.map(pair)
            output = compositor.process([pair], [result])
            pair.release()

        assert output is not None
        frame = output.frame
        height, width = frame.shape[:2]

        plot_region = frame[int(height * 0.75):, :]
        bright_pixels = np.sum(plot_region > 100)
        print(f"\nFramerate plot region: {bright_pixels} bright pixels")
        assert bright_pixels > 1000

        ft_region = frame[int(height * 0.45):int(height * 0.65), :]
        ft_bright = np.sum(ft_region > 100)
        print(f"Frametime plot region: {ft_bright} bright pixels")
        assert ft_bright > 500

    def test_framerate_plot_modifies_output(self, qapp, test_video, plot_style, text_style):
        """Verify framerate plot actually draws pixels."""
        analyzer = DuplicateDetector()

        compositor_no_plots = SimpleCompositor(
            video_count=1,
            video_fps=[test_video.fps],
            output_width=1280,
            output_height=720,
        )

        compositor_with_plot = SimpleCompositor(
            video_count=1,
            video_fps=[test_video.fps],
            output_width=1280,
            output_height=720,
            framerate_plots=[FrameratePlot(plot_style, max_fps=60.0)],
        )

        # Process through both compositors simultaneously
        source = SequentialFrameSource(test_video)
        output_no_plot = None
        output_with_plot = None
        for i, pair in enumerate(source):
            if i >= 30:
                pair.release()
                break
            result = analyzer.map(pair)
            output_no_plot = compositor_no_plots.process([pair], [result])
            output_with_plot = compositor_with_plot.process([pair], [result])
            pair.release()

        assert output_no_plot is not None
        assert output_with_plot is not None
        frame_no_plot = output_no_plot.frame
        frame_with_plot = output_with_plot.frame

        diff = np.abs(frame_with_plot.astype(int) - frame_no_plot.astype(int))
        changed_pixels = np.sum(diff > 0)

        assert changed_pixels > 5000, (
            f"Framerate plot should modify output but only {changed_pixels} pixels changed"
        )

    def test_frametime_plot_modifies_output(self, qapp, test_video, plot_style, text_style):
        """Verify frametime plot actually draws pixels."""
        analyzer = DuplicateDetector()

        compositor_fps_only = SimpleCompositor(
            video_count=1,
            video_fps=[test_video.fps],
            output_width=1280,
            output_height=720,
            framerate_plots=[FrameratePlot(plot_style, max_fps=60.0)],
        )

        compositor_with_both = SimpleCompositor(
            video_count=1,
            video_fps=[test_video.fps],
            output_width=1280,
            output_height=720,
            framerate_plots=[FrameratePlot(plot_style, max_fps=60.0)],
            frametime_plots=[FrametimePlot(plot_style, max_ms=50.0)],
        )

        source = SequentialFrameSource(test_video)
        output_fps_only = None
        output_with_both = None
        for i, pair in enumerate(source):
            if i >= 30:
                pair.release()
                break
            result = analyzer.map(pair)
            output_fps_only = compositor_fps_only.process([pair], [result])
            output_with_both = compositor_with_both.process([pair], [result])
            pair.release()

        assert output_fps_only is not None
        assert output_with_both is not None
        frame_fps_only = output_fps_only.frame
        frame_with_both = output_with_both.frame

        diff = np.abs(frame_with_both.astype(int) - frame_fps_only.astype(int))
        changed_pixels = np.sum(diff > 0)

        assert changed_pixels > 1000, (
            f"Frametime plot should modify output but only {changed_pixels} pixels changed"
        )
