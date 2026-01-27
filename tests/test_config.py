"""Tests for the config module.

Tests cover:
- Reference types (GlobalRef, VideoRef)
- Position and Size with coordinate translation
- Layout computation
- YAML serialization round-trip
- ConfigStore observable pattern
- CoordinateSystem translations
"""

from __future__ import annotations

from pathlib import Path

import pytest

from trdrop.config import (
    ConfigStore,
    CoordinateSystem,
    FrameLayout,
    GlobalRef,
    LayoutConfig,
    LayoutMode,
    Position,
    PresetConfig,
    Size,
    VideoOverlayConfig,
    VideoRef,
    VideoRegion,
    ViewportState,
    compute_layout,
    load_preset,
    preset_from_yaml,
    preset_to_yaml,
    save_preset,
)


class TestReferenceTypes:
    """Tests for GlobalRef and VideoRef."""

    def test_global_ref_repr(self) -> None:
        ref = GlobalRef()
        assert repr(ref) == "GlobalRef()"

    def test_video_ref_repr(self) -> None:
        ref = VideoRef(0)
        assert repr(ref) == "VideoRef(0)"
        ref2 = VideoRef(3)
        assert repr(ref2) == "VideoRef(3)"

    def test_video_ref_equality(self) -> None:
        assert VideoRef(0) == VideoRef(0)
        assert VideoRef(0) != VideoRef(1)
        assert GlobalRef() == GlobalRef()
        assert GlobalRef() != VideoRef(0)

    def test_reference_frozen(self) -> None:
        ref = VideoRef(0)
        with pytest.raises(AttributeError):
            ref.index = 1  # type: ignore


class TestPosition:
    """Tests for Position coordinate translation."""

    @pytest.fixture
    def simple_layout(self) -> FrameLayout:
        """2 videos side by side, 1920x1080."""
        return FrameLayout(
            regions=(
                VideoRegion(index=0, x=0.0, y=0.0, width=0.5, height=1.0),
                VideoRegion(index=1, x=0.5, y=0.0, width=0.5, height=1.0),
            ),
            output_width=1920,
            output_height=1080,
        )

    def test_global_position_to_global(self, simple_layout: FrameLayout) -> None:
        pos = Position(0.5, 0.5, GlobalRef())
        gx, gy = pos.to_global(simple_layout)
        assert gx == 0.5
        assert gy == 0.5

    def test_video_position_to_global(self, simple_layout: FrameLayout) -> None:
        # Position at (0.1, 0.1) within video 0 (left half)
        pos = Position(0.1, 0.1, VideoRef(0))
        gx, gy = pos.to_global(simple_layout)
        # Video 0 occupies x=0.0-0.5, so 0.1 * 0.5 = 0.05
        assert gx == pytest.approx(0.05)
        assert gy == pytest.approx(0.1)

    def test_video_position_to_global_video1(self, simple_layout: FrameLayout) -> None:
        # Position at (0.1, 0.1) within video 1 (right half)
        pos = Position(0.1, 0.1, VideoRef(1))
        gx, gy = pos.to_global(simple_layout)
        # Video 1 starts at x=0.5, so 0.5 + 0.1 * 0.5 = 0.55
        assert gx == pytest.approx(0.55)
        assert gy == pytest.approx(0.1)

    def test_position_to_pixels(self, simple_layout: FrameLayout) -> None:
        pos = Position(0.5, 0.5, GlobalRef())
        px, py = pos.to_pixels(simple_layout)
        assert px == 960
        assert py == 540

    def test_position_from_global(self, simple_layout: FrameLayout) -> None:
        # Convert global (0.25, 0.5) to video 0 local
        pos = Position.from_global(0.25, 0.5, VideoRef(0), simple_layout)
        # Video 0 is x=0.0-0.5, so local x = 0.25 / 0.5 = 0.5
        assert pos.x == pytest.approx(0.5)
        assert pos.y == pytest.approx(0.5)
        assert pos.ref == VideoRef(0)

    def test_position_with_ref(self, simple_layout: FrameLayout) -> None:
        # Start with global position
        pos = Position(0.25, 0.5, GlobalRef())
        # Convert to video 0 reference
        pos_local = pos.with_ref(VideoRef(0), simple_layout)
        assert pos_local.x == pytest.approx(0.5)
        assert pos_local.y == pytest.approx(0.5)
        assert pos_local.ref == VideoRef(0)

    def test_position_round_trip(self, simple_layout: FrameLayout) -> None:
        original = Position(0.3, 0.7, VideoRef(0))
        # To global and back
        gx, gy = original.to_global(simple_layout)
        restored = Position.from_global(gx, gy, VideoRef(0), simple_layout)
        assert restored.x == pytest.approx(original.x)
        assert restored.y == pytest.approx(original.y)


class TestSize:
    """Tests for Size coordinate translation."""

    @pytest.fixture
    def simple_layout(self) -> FrameLayout:
        return FrameLayout(
            regions=(
                VideoRegion(index=0, x=0.0, y=0.0, width=0.5, height=1.0),
                VideoRegion(index=1, x=0.5, y=0.0, width=0.5, height=1.0),
            ),
            output_width=1920,
            output_height=1080,
        )

    def test_global_size_to_global(self, simple_layout: FrameLayout) -> None:
        size = Size(0.5, 0.25, GlobalRef())
        gw, gh = size.to_global(simple_layout)
        assert gw == 0.5
        assert gh == 0.25

    def test_video_size_to_global(self, simple_layout: FrameLayout) -> None:
        # Size of (0.5, 0.5) within video 0 (which is 0.5 wide)
        size = Size(0.5, 0.5, VideoRef(0))
        gw, gh = size.to_global(simple_layout)
        # 0.5 * 0.5 = 0.25 (half of video width = quarter of total)
        assert gw == pytest.approx(0.25)
        assert gh == pytest.approx(0.5)

    def test_size_to_pixels(self, simple_layout: FrameLayout) -> None:
        size = Size(0.5, 0.25, GlobalRef())
        pw, ph = size.to_pixels(simple_layout)
        assert pw == 960
        assert ph == 270


class TestLayout:
    """Tests for layout computation."""

    def test_single_video_layout(self) -> None:
        layout = compute_layout(1, LayoutConfig(mode=LayoutMode.GRID), 1920, 1080)
        assert len(layout.regions) == 1
        assert layout.regions[0].x == 0.0
        assert layout.regions[0].y == 0.0
        assert layout.regions[0].width == 1.0
        assert layout.regions[0].height == 1.0

    def test_two_videos_grid(self) -> None:
        layout = compute_layout(2, LayoutConfig(mode=LayoutMode.GRID), 1920, 1080)
        assert len(layout.regions) == 2
        # Side by side
        assert layout.regions[0].width == 0.5
        assert layout.regions[1].x == 0.5

    def test_four_videos_grid(self) -> None:
        layout = compute_layout(4, LayoutConfig(mode=LayoutMode.GRID), 1920, 1080)
        assert len(layout.regions) == 4
        # 2x2 grid
        assert layout.regions[0].rect == (0.0, 0.0, 0.5, 0.5)
        assert layout.regions[1].rect == (0.5, 0.0, 0.5, 0.5)
        assert layout.regions[2].rect == (0.0, 0.5, 0.5, 0.5)
        assert layout.regions[3].rect == (0.5, 0.5, 0.5, 0.5)

    def test_horizontal_layout(self) -> None:
        layout = compute_layout(3, LayoutConfig(mode=LayoutMode.HORIZONTAL), 1920, 1080)
        assert len(layout.regions) == 3
        expected_width = 1.0 / 3
        for i, region in enumerate(layout.regions):
            assert region.width == pytest.approx(expected_width)
            assert region.height == 1.0
            assert region.x == pytest.approx(i * expected_width)

    def test_vertical_layout(self) -> None:
        layout = compute_layout(2, LayoutConfig(mode=LayoutMode.VERTICAL), 1920, 1080)
        assert len(layout.regions) == 2
        assert layout.regions[0].rect == (0.0, 0.0, 1.0, 0.5)
        assert layout.regions[1].rect == (0.0, 0.5, 1.0, 0.5)

    def test_layout_with_spacing(self) -> None:
        layout = compute_layout(
            2, LayoutConfig(mode=LayoutMode.GRID, spacing=0.02), 1920, 1080
        )
        assert len(layout.regions) == 2
        # With 0.02 spacing, each video is (1.0 - 0.02) / 2 = 0.49
        assert layout.regions[0].width == pytest.approx(0.49)
        assert layout.regions[1].x == pytest.approx(0.51)

    def test_hit_test(self) -> None:
        layout = compute_layout(2, LayoutConfig(mode=LayoutMode.GRID), 1920, 1080)
        assert layout.hit_test(0.25, 0.5) == 0  # Left half
        assert layout.hit_test(0.75, 0.5) == 1  # Right half
        assert layout.hit_test(-0.1, 0.5) is None  # Outside

    def test_empty_layout(self) -> None:
        layout = compute_layout(0, LayoutConfig(), 1920, 1080)
        assert len(layout.regions) == 0


class TestSerialization:
    """Tests for YAML serialization."""

    def test_preset_round_trip(self) -> None:
        config = PresetConfig()
        config.processing.window_size = 120
        config.rendering.fps_plot.visible = False
        config.export.resolution = (3840, 2160)

        yaml_str = preset_to_yaml(config)
        loaded = preset_from_yaml(yaml_str)

        assert loaded.processing.window_size == 120
        assert loaded.rendering.fps_plot.visible is False
        assert loaded.export.resolution == (3840, 2160)

    def test_position_serialization(self) -> None:
        config = PresetConfig()
        config.videos[0] = VideoOverlayConfig()
        config.videos[0].fps_text.position = Position(0.1, 0.2, VideoRef(0))

        yaml_str = preset_to_yaml(config)
        loaded = preset_from_yaml(yaml_str)

        pos = loaded.videos[0].fps_text.position
        assert pos.x == 0.1
        assert pos.y == 0.2
        assert pos.ref == VideoRef(0)

    def test_global_ref_serialization(self) -> None:
        config = PresetConfig()
        config.rendering.fps_plot.position = Position(0.5, 0.9, GlobalRef())

        yaml_str = preset_to_yaml(config)
        loaded = preset_from_yaml(yaml_str)

        pos = loaded.rendering.fps_plot.position
        assert pos.ref == GlobalRef()

    def test_empty_yaml(self) -> None:
        loaded = preset_from_yaml("")
        assert isinstance(loaded, PresetConfig)

    def test_save_and_load(self, tmp_path: Path) -> None:
        config = PresetConfig()
        config.processing.duplicate_threshold = 0.05
        path = tmp_path / "test_preset.yaml"

        save_preset(config, path)
        loaded = load_preset(path)

        assert loaded.processing.duplicate_threshold == 0.05

    def test_sparse_videos_serialization(self) -> None:
        config = PresetConfig()
        config.videos[0] = VideoOverlayConfig()
        config.videos[2] = VideoOverlayConfig()  # Skip index 1

        yaml_str = preset_to_yaml(config)
        loaded = preset_from_yaml(yaml_str)

        assert 0 in loaded.videos
        assert 1 not in loaded.videos
        assert 2 in loaded.videos


class TestConfigStore:
    """Tests for the observable ConfigStore."""

    def test_initial_config(self) -> None:
        store = ConfigStore()
        assert isinstance(store.config, PresetConfig)

    def test_initial_config_provided(self) -> None:
        config = PresetConfig()
        config.processing.window_size = 100
        store = ConfigStore(config)
        assert store.config.processing.window_size == 100

    def test_modify_notifies(self) -> None:
        store = ConfigStore()
        notifications: list[PresetConfig] = []

        store.subscribe(lambda c: notifications.append(c))
        store.modify(lambda c: setattr(c.processing, "window_size", 200))

        assert len(notifications) == 1
        assert notifications[0].processing.window_size == 200

    def test_edit_context_manager(self) -> None:
        store = ConfigStore()
        notifications: list[PresetConfig] = []

        store.subscribe(lambda c: notifications.append(c))

        with store.edit() as config:
            config.processing.window_size = 300
            config.rendering.fps_plot.visible = False

        assert len(notifications) == 1
        assert store.config.processing.window_size == 300
        assert store.config.rendering.fps_plot.visible is False

    def test_replace_notifies(self) -> None:
        store = ConfigStore()
        notifications: list[PresetConfig] = []

        store.subscribe(lambda c: notifications.append(c))

        new_config = PresetConfig()
        new_config.processing.window_size = 400
        store.replace(new_config)

        assert len(notifications) == 1
        assert store.config.processing.window_size == 400

    def test_unsubscribe(self) -> None:
        store = ConfigStore()
        count = [0]

        def counter(c: PresetConfig) -> None:
            count[0] += 1

        unsubscribe = store.subscribe(counter)
        store.modify(lambda c: None)
        assert count[0] == 1

        unsubscribe()
        store.modify(lambda c: None)
        assert count[0] == 1  # No more notifications

    def test_multiple_subscribers(self) -> None:
        store = ConfigStore()
        counts = [0, 0]

        store.subscribe(lambda c: counts.__setitem__(0, counts[0] + 1))
        store.subscribe(lambda c: counts.__setitem__(1, counts[1] + 1))

        store.modify(lambda c: None)

        assert counts[0] == 1
        assert counts[1] == 1

    def test_subscriber_receives_current_config(self) -> None:
        store = ConfigStore()
        store.modify(lambda c: setattr(c.processing, "window_size", 100))

        received: list[int] = []
        store.subscribe(lambda c: received.append(c.processing.window_size))
        store.modify(lambda c: setattr(c.processing, "window_size", 200))

        assert received == [200]


class TestCoordinateSystem:
    """Tests for CoordinateSystem translations."""

    @pytest.fixture
    def coords(self) -> CoordinateSystem:
        layout = compute_layout(2, LayoutConfig(mode=LayoutMode.GRID), 1920, 1080)
        return CoordinateSystem(layout)

    @pytest.fixture
    def viewport(self) -> ViewportState:
        return ViewportState(width=800, height=450, pan_x=0.0, pan_y=0.0, zoom=1.0)

    def test_position_to_global(self, coords: CoordinateSystem) -> None:
        pos = Position(0.1, 0.1, VideoRef(0))
        gx, gy = coords.position_to_global(pos)
        assert gx == pytest.approx(0.05)
        assert gy == pytest.approx(0.1)

    def test_screen_to_global_no_zoom(
        self, coords: CoordinateSystem, viewport: ViewportState
    ) -> None:
        # Click at center of viewport
        gx, gy = coords.screen_to_global(400, 225, viewport)
        assert gx == pytest.approx(0.5)
        assert gy == pytest.approx(0.5)

    def test_screen_to_global_with_zoom(
        self, coords: CoordinateSystem, viewport: ViewportState
    ) -> None:
        viewport = ViewportState(width=800, height=450, pan_x=0.0, pan_y=0.0, zoom=2.0)
        # At 2x zoom, viewport shows 0.0-0.5 range
        gx, gy = coords.screen_to_global(400, 225, viewport)
        assert gx == pytest.approx(0.25)
        assert gy == pytest.approx(0.25)

    def test_screen_to_global_with_pan(
        self, coords: CoordinateSystem, viewport: ViewportState
    ) -> None:
        viewport = ViewportState(width=800, height=450, pan_x=0.2, pan_y=0.1, zoom=1.0)
        gx, gy = coords.screen_to_global(0, 0, viewport)
        assert gx == pytest.approx(0.2)
        assert gy == pytest.approx(0.1)

    def test_global_to_screen(
        self, coords: CoordinateSystem, viewport: ViewportState
    ) -> None:
        sx, sy = coords.global_to_screen(0.5, 0.5, viewport)
        assert sx == pytest.approx(400)
        assert sy == pytest.approx(225)

    def test_screen_to_video_index(
        self, coords: CoordinateSystem, viewport: ViewportState
    ) -> None:
        # Click in left half -> video 0
        assert coords.screen_to_video_index(200, 225, viewport) == 0
        # Click in right half -> video 1
        assert coords.screen_to_video_index(600, 225, viewport) == 1

    def test_video_ref_helper(self, coords: CoordinateSystem) -> None:
        ref = coords.video_ref(2)
        assert ref == VideoRef(2)

    def test_global_ref_helper(self, coords: CoordinateSystem) -> None:
        ref = coords.global_ref()
        assert ref == GlobalRef()
