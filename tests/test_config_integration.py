"""Integration tests for config-based pipeline.

Tests that PresetConfig flows correctly through:
1. Compositor creation and layout computation
2. Overlay positioning from config
3. Engine execution with config access
4. YAML round-trip preserving behavior
"""

from __future__ import annotations

import sys

import numpy as np
import pytest
from PyQt6.QtGui import QGuiApplication

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.compositor.simple import SimpleCompositor
from trdrop.config import (
    ConfigStore,
    FpsTextConfig,
    GlobalRef,
    LayoutConfig,
    LayoutMode,
    Position,
    PresetConfig,
    Size,
    VideoOverlayConfig,
    VideoRef,
    load_preset,
    save_preset,
)
from trdrop.engine import StreamingEngine
from trdrop.source.sequential import SequentialFrameSource
from trdrop.video.reader import PyAVReader


@pytest.fixture(scope="module")
def qapp():
    """QGuiApplication for Qt-based rendering."""
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    return app


@pytest.fixture(scope="module")
def test_video(tmp_path_factory, qapp):
    """Generate a test video for integration tests."""
    tmp_dir = tmp_path_factory.mktemp("videos")
    video_path = tmp_dir / "test_30in60.mp4"

    config = VideoConfig(
        container_fps=60,
        content_fps=30,
        duration_sec=1.0,
        width=640,
        height=480,
        pattern=PatternType.COUNTER,
    )
    VideoGenerator(config).write(video_path)
    return video_path


class TestCompositorWithConfig:
    """Test compositor behavior with PresetConfig."""

    def test_compositor_uses_config_layout_mode(self, qapp, test_video):
        """Verify compositor respects layout mode from config."""
        reader = PyAVReader(test_video)

        # Create config with HORIZONTAL layout
        config = PresetConfig()
        config.rendering.layout = LayoutConfig(mode=LayoutMode.HORIZONTAL)

        compositor = SimpleCompositor(
            video_count=2,
            video_fps=[reader.fps, reader.fps],
            output_width=1280,
            output_height=720,
            config=config,
        )

        layout = compositor.layout
        assert layout.video_count == 2

        # Horizontal: videos side by side
        region0 = layout.get_region(0)
        region1 = layout.get_region(1)

        assert region0.x == 0.0
        assert region0.width == 0.5
        assert region1.x == 0.5
        assert region1.width == 0.5

        reader.close()

    def test_plot_font_sizes_are_tuned_for_dense_four_up_layouts(self, qapp, test_video):
        """Verify 4-up keeps framerate text stable while shrinking frametime labels."""
        reader = PyAVReader(test_video)

        config = PresetConfig()
        config.rendering.fps_plot.visible = True
        config.rendering.frametime_plot.visible = True

        single = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=1920,
            output_height=1080,
            config=config,
        )
        four_up = SimpleCompositor(
            video_count=4,
            video_fps=[reader.fps] * 4,
            output_width=1920,
            output_height=1080,
            config=config,
        )

        assert single._framerate_plots is not None
        assert four_up._framerate_plots is not None
        assert single._frametime_plots is not None
        assert four_up._frametime_plots is not None

        assert single._framerate_plots[0]._style.font.pixelSize() == \
            four_up._framerate_plots[0]._style.font.pixelSize()
        assert single._framerate_plots[0]._style.title_font is not None
        assert four_up._framerate_plots[0]._style.title_font is not None
        assert single._framerate_plots[0]._style.title_font.pixelSize() == \
            four_up._framerate_plots[0]._style.title_font.pixelSize()
        assert single._framerate_plots[0]._style.line_width == 5
        assert four_up._framerate_plots[0]._style.line_width == 5

        assert single._frametime_plots[0]._style.font.pixelSize() > \
            four_up._frametime_plots[0]._style.font.pixelSize()
        assert single._frametime_plots[0]._style.title_font is not None
        assert four_up._frametime_plots[0]._style.title_font is not None
        assert single._frametime_plots[0]._style.title_font.pixelSize() == \
            four_up._frametime_plots[0]._style.title_font.pixelSize()
        assert single._frametime_plots[0]._time_anchor == 1.0
        assert four_up._frametime_plots[0]._time_anchor == 1.0

        reader.close()

    def test_compositor_uses_config_grid_layout(self, qapp, test_video):
        """Verify compositor respects GRID layout from config."""
        reader = PyAVReader(test_video)

        config = PresetConfig()
        config.rendering.layout = LayoutConfig(mode=LayoutMode.GRID)

        compositor = SimpleCompositor(
            video_count=4,
            video_fps=[reader.fps] * 4,
            output_width=1920,
            output_height=1080,
            config=config,
        )

        layout = compositor.layout
        assert layout.video_count == 4

        # Grid: 2x2 arrangement
        region0 = layout.get_region(0)
        region1 = layout.get_region(1)
        region2 = layout.get_region(2)
        region3 = layout.get_region(3)

        # Top-left
        assert region0.x == 0.0
        assert region0.y == 0.0
        assert region0.width == 0.5
        assert region0.height == 0.5

        # Top-right
        assert region1.x == 0.5
        assert region1.y == 0.0

        # Bottom-left
        assert region2.x == 0.0
        assert region2.y == 0.5

        # Bottom-right
        assert region3.x == 0.5
        assert region3.y == 0.5

        reader.close()

    def test_compositor_exposes_config(self, qapp, test_video):
        """Verify compositor exposes its config for external access."""
        reader = PyAVReader(test_video)

        config = PresetConfig()
        config.processing.duplicate_threshold = 0.05

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=1280,
            output_height=720,
            config=config,
        )

        assert compositor.config is config
        assert compositor.config.processing.duplicate_threshold == 0.05

        reader.close()

    def test_compositor_creates_overlays_from_config(self, qapp, test_video):
        """Verify compositor creates overlay objects from config when not provided."""
        reader = PyAVReader(test_video)
        source = SequentialFrameSource(reader)
        analyzer = DuplicateDetector()

        # Config with visible FPS plot
        config = PresetConfig()
        config.rendering.fps_plot.visible = True
        config.rendering.fps_plot.position = Position(0.1, 0.8, GlobalRef())
        config.rendering.fps_plot.size = Size(0.8, 0.15, GlobalRef())

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=1280,
            output_height=720,
            config=config,
            # No legacy overlay objects passed
        )

        # Process some frames
        output = None
        for i, pair in enumerate(source):
            if i >= 10:
                pair.release()
                break
            result = analyzer.map(pair)
            output = compositor.process([pair], [result])
            pair.release()

        assert output is not None
        frame = output.frame

        # Check that plot region has content (not black)
        # Plot at 80% down, 10% from left, 80% width, 15% height
        plot_y = int(720 * 0.8)
        plot_x = int(1280 * 0.1)
        plot_h = int(720 * 0.15)
        plot_w = int(1280 * 0.8)

        plot_region = frame[plot_y:plot_y + plot_h, plot_x:plot_x + plot_w]
        non_black = np.sum(plot_region > 20)

        assert non_black > 100, "FPS plot should render content at config position"

        source.close()


class TestEngineWithConfig:
    """Test engine exposes config and layout."""

    def test_engine_exposes_layout(self, qapp, test_video):
        """Verify engine exposes compositor layout."""
        reader = PyAVReader(test_video)
        source = SequentialFrameSource(reader)

        config = PresetConfig()
        config.rendering.layout = LayoutConfig(mode=LayoutMode.HORIZONTAL)

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=1280,
            output_height=720,
            config=config,
        )

        engine = StreamingEngine(
            sources=[source],
            analyzers=[DuplicateDetector()],
            compositor=compositor,
            exporters=[],
        )

        assert engine.layout is not None
        assert engine.layout.video_count == 1
        assert engine.layout.output_width == 1280
        assert engine.layout.output_height == 720

        source.close()

    def test_engine_exposes_config(self, qapp, test_video):
        """Verify engine exposes compositor config."""
        reader = PyAVReader(test_video)
        source = SequentialFrameSource(reader)

        config = PresetConfig()
        config.processing.window_size = 120

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=1280,
            output_height=720,
            config=config,
        )

        engine = StreamingEngine(
            sources=[source],
            analyzers=[DuplicateDetector()],
            compositor=compositor,
            exporters=[],
        )

        assert engine.config is not None
        assert engine.config is config
        assert engine.config.processing.window_size == 120

        source.close()


class TestConfigYamlRoundTrip:
    """Test that config survives YAML serialization and still works."""

    def test_saved_config_produces_same_layout(self, qapp, test_video, tmp_path):
        """Verify config loaded from YAML produces identical layout."""
        reader = PyAVReader(test_video)

        # Create config with specific settings
        original = PresetConfig()
        original.rendering.layout = LayoutConfig(
            mode=LayoutMode.GRID,
            spacing=0.02,
        )
        original.rendering.fps_plot.position = Position(0.05, 0.75, GlobalRef())
        original.rendering.fps_plot.size = Size(0.9, 0.2, GlobalRef())

        # Save and reload
        yaml_path = tmp_path / "test_config.yaml"
        save_preset(original, yaml_path)
        loaded = load_preset(yaml_path)

        # Create compositors with each
        compositor_original = SimpleCompositor(
            video_count=4,
            video_fps=[reader.fps] * 4,
            output_width=1920,
            output_height=1080,
            config=original,
        )

        compositor_loaded = SimpleCompositor(
            video_count=4,
            video_fps=[reader.fps] * 4,
            output_width=1920,
            output_height=1080,
            config=loaded,
        )

        # Layouts should match
        layout_orig = compositor_original.layout
        layout_loaded = compositor_loaded.layout

        for i in range(4):
            r_orig = layout_orig.get_region(i)
            r_loaded = layout_loaded.get_region(i)

            assert r_orig.x == pytest.approx(r_loaded.x, abs=0.001)
            assert r_orig.y == pytest.approx(r_loaded.y, abs=0.001)
            assert r_orig.width == pytest.approx(r_loaded.width, abs=0.001)
            assert r_orig.height == pytest.approx(r_loaded.height, abs=0.001)

        reader.close()

    def test_video_overlay_positions_survive_yaml(self, qapp, tmp_path):
        """Verify per-video overlay positions survive YAML round-trip."""
        original = PresetConfig()

        # Set custom positions for video overlays
        original.videos[0] = VideoOverlayConfig(
            fps_text=FpsTextConfig(
                position=Position(0.1, 0.1, VideoRef(0)),
                visible=True,
            ),
        )
        original.videos[1] = VideoOverlayConfig(
            fps_text=FpsTextConfig(
                position=Position(0.2, 0.2, VideoRef(1)),
                visible=False,
            ),
        )

        # Save and reload
        yaml_path = tmp_path / "video_config.yaml"
        save_preset(original, yaml_path)
        loaded = load_preset(yaml_path)

        # Verify positions
        assert loaded.videos[0].fps_text.position.x == 0.1
        assert loaded.videos[0].fps_text.position.y == 0.1
        assert isinstance(loaded.videos[0].fps_text.position.ref, VideoRef)
        assert loaded.videos[0].fps_text.position.ref.index == 0
        assert loaded.videos[0].fps_text.visible is True

        assert loaded.videos[1].fps_text.position.x == 0.2
        assert loaded.videos[1].fps_text.position.y == 0.2
        assert isinstance(loaded.videos[1].fps_text.position.ref, VideoRef)
        assert loaded.videos[1].fps_text.position.ref.index == 1
        assert loaded.videos[1].fps_text.visible is False


class TestConfigStoreIntegration:
    """Test ConfigStore works with compositor updates."""

    def test_config_store_modifications_reflected(self, qapp, test_video):
        """Verify ConfigStore modifications are visible to compositor."""
        reader = PyAVReader(test_video)

        store = ConfigStore()

        # Modify via store
        with store.edit() as cfg:
            cfg.rendering.layout = LayoutConfig(mode=LayoutMode.VERTICAL)
            cfg.rendering.fps_plot.visible = False

        # Create compositor with store's config
        compositor = SimpleCompositor(
            video_count=2,
            video_fps=[reader.fps, reader.fps],
            output_width=1280,
            output_height=720,
            config=store.config,
        )

        # Verify layout is vertical
        layout = compositor.layout
        region0 = layout.get_region(0)
        region1 = layout.get_region(1)

        # Vertical: videos stacked
        assert region0.y == 0.0
        assert region0.height == 0.5
        assert region1.y == 0.5
        assert region1.height == 0.5

        reader.close()

    def test_subscriber_notified_on_config_change(self, qapp):
        """Verify subscribers receive notifications on config changes."""
        store = ConfigStore()
        notifications = []

        def on_change(cfg: PresetConfig) -> None:
            notifications.append(cfg.rendering.layout.mode)

        store.subscribe(on_change)

        # Modify config
        store.modify(
            lambda c: setattr(c.rendering, 'layout', LayoutConfig(mode=LayoutMode.GRID))
        )

        assert len(notifications) == 1
        assert notifications[0] == LayoutMode.GRID

        # Another modification
        with store.edit() as cfg:
            cfg.rendering.layout = LayoutConfig(mode=LayoutMode.HORIZONTAL)

        assert len(notifications) == 2
        assert notifications[1] == LayoutMode.HORIZONTAL


class TestOverlayPositionFromConfig:
    """Test overlay elements render at config-specified positions."""

    def test_fps_text_position_from_config(self, qapp, test_video):
        """Verify FPS text renders at position specified in config."""
        reader = PyAVReader(test_video)
        source = SequentialFrameSource(reader)
        analyzer = DuplicateDetector()

        config = PresetConfig()
        # Position FPS text at bottom-right corner
        config.videos[0] = VideoOverlayConfig(
            fps_text=FpsTextConfig(
                position=Position(0.7, 0.9, GlobalRef()),
                visible=True,
                font_size=0.05,  # Large enough to see
            ),
        )
        config.rendering.fps_plot.visible = False  # Disable plot

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=1280,
            output_height=720,
            config=config,
        )

        # Process frames
        output = None
        for i, pair in enumerate(source):
            if i >= 20:
                pair.release()
                break
            result = analyzer.map(pair)
            output = compositor.process([pair], [result])
            pair.release()

        assert output is not None
        frame = output.frame

        # Check bottom-right region has text (non-black pixels)
        text_y = int(720 * 0.85)  # Slightly above 0.9 for text baseline
        text_x = int(1280 * 0.7)
        text_region = frame[text_y:text_y + 50, text_x:text_x + 200]
        non_black = np.sum(text_region > 50)

        # Check top-left region is mostly black (no text there)
        top_left = frame[0:100, 0:200]
        top_left_bright = np.sum(top_left > 50)

        assert non_black > 100, "FPS text should render at config position"
        # Top-left should have less bright pixels than text region
        assert top_left_bright < non_black, "Text should not be at default position"

        source.close()

    def test_fps_plot_position_from_config(self, qapp, test_video):
        """Verify FPS plot renders at position specified in config."""
        reader = PyAVReader(test_video)
        source = SequentialFrameSource(reader)
        analyzer = DuplicateDetector()

        # Create two compositors: one with custom position, one with default
        config_custom = PresetConfig()
        config_custom.rendering.fps_plot.position = Position(0.1, 0.05, GlobalRef())
        config_custom.rendering.fps_plot.size = Size(0.8, 0.2, GlobalRef())
        config_custom.rendering.fps_plot.visible = True

        config_default = PresetConfig()
        config_default.rendering.fps_plot.position = Position(0.05, 0.85, GlobalRef())
        config_default.rendering.fps_plot.size = Size(0.9, 0.12, GlobalRef())
        config_default.rendering.fps_plot.visible = True

        compositor_custom = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=1280,
            output_height=720,
            config=config_custom,
        )

        compositor_default = SimpleCompositor(
            video_count=1,
            video_fps=[reader.fps],
            output_width=1280,
            output_height=720,
            config=config_default,
        )

        # Process same frames through both
        output_custom = None
        output_default = None

        for i, pair in enumerate(source):
            if i >= 20:
                pair.release()
                break
            result = analyzer.map(pair)
            output_custom = compositor_custom.process([pair], [result])
            output_default = compositor_default.process([pair], [result])
            pair.release()

        assert output_custom is not None
        assert output_default is not None

        frame_custom = output_custom.frame
        frame_default = output_default.frame

        # Check top region of custom (where plot should be)
        top_y = int(720 * 0.05)
        top_h = int(720 * 0.2)
        custom_top = frame_custom[top_y:top_y + top_h, :]
        default_top = frame_default[top_y:top_y + top_h, :]

        # Check bottom region (where default plot should be)
        bottom_y = int(720 * 0.85)
        bottom_h = int(720 * 0.12)
        custom_bottom = frame_custom[bottom_y:bottom_y + bottom_h, :]
        default_bottom = frame_default[bottom_y:bottom_y + bottom_h, :]

        # Custom should have more content in top, less in bottom
        # Default should have more content in bottom, less in top
        custom_top_bright = np.sum(custom_top > 30)
        default_top_bright = np.sum(default_top > 30)
        custom_bottom_bright = np.sum(custom_bottom > 30)
        default_bottom_bright = np.sum(default_bottom > 30)

        # The config positions should differ - custom has plot at top
        assert custom_top_bright > default_top_bright, \
            "Custom config should render plot at top"
        assert default_bottom_bright > custom_bottom_bright, \
            "Default config should render plot at bottom"

        source.close()

    def test_multi_video_frametime_bounds_avoid_combined_framerate(
        self, qapp, test_video
    ):
        """Verify separate frametime plots avoid the combined framerate plot."""
        reader = PyAVReader(test_video)

        for video_count in (2, 3, 4):
            config = PresetConfig()
            config.rendering.fps_plot.visible = True
            config.rendering.frametime_plot.visible = True

            compositor = SimpleCompositor(
                video_count=video_count,
                video_fps=[reader.fps] * video_count,
                output_width=1920,
                output_height=1080,
                config=config,
            )

            combined_fr_bounds = compositor._combined_framerate_plot_bounds()

            for i in range(video_count):
                bounds = compositor._frametime_plot_bounds(i)
                video_px, video_py, video_pw, video_ph = compositor._video_pixel_bounds(i)

                assert bounds.left() >= video_px
                assert bounds.right() <= video_px + video_pw
                assert bounds.top() >= video_py
                assert bounds.bottom() <= video_py + video_ph
                assert not bounds.intersects(combined_fr_bounds)

        reader.close()
