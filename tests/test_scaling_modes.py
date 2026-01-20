"""Tests for scaling modes across different video count configurations.

Tests all combinations of:
- Scale modes: CROP, FIT, STRETCH
- Video counts: 1, 2, 3, 4 (layouts: 1:1:1:1, 1:1:1, 1:1, single)
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pytest
from PyQt6.QtGui import QGuiApplication

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.compositor import ScaleMode, SimpleCompositor
from trdrop.types.frames import FramePair, FrameView
from trdrop.types.metrics import FrameMetrics


class TestScalingModes:
    """Test scaling mode behavior with different video counts."""

    @pytest.fixture(scope="class")
    def qapp(self):
        """Create QGuiApplication for QPainter operations."""
        app = QGuiApplication.instance()
        if app is None:
            app = QGuiApplication(sys.argv)
        return app

    @pytest.mark.parametrize(
        "scale_mode",
        [ScaleMode.CROP, ScaleMode.FIT, ScaleMode.STRETCH],
        ids=["crop", "fit", "stretch"],
    )
    @pytest.mark.parametrize(
        "video_count",
        [1, 2, 3, 4],
        ids=["1video", "2videos", "3videos", "4videos"],
    )
    def test_compositor_produces_valid_output(
        self,
        qapp,
        scale_mode: ScaleMode,
        video_count: int,
    ) -> None:
        """Compositor produces correctly sized output for all mode/count combos."""
        output_width = 1280
        output_height = 720
        source_width = 640
        source_height = 480

        compositor = SimpleCompositor(
            video_count=video_count,
            video_fps=[60.0] * video_count,
            output_width=output_width,
            output_height=output_height,
            scale_mode=scale_mode,
        )

        # Create dummy frames
        pairs = []
        results = []
        for i in range(video_count):
            frame_data = np.full(
                (source_height, source_width, 3),
                fill_value=(50 + i * 50, 100, 150),
                dtype=np.uint8,
            )
            view = FrameView(_data=frame_data, index=0, pts=0)
            pair = FramePair(prev=view, curr=view, _on_release=lambda: None)
            pairs.append(pair)
            results.append(FrameMetrics(frame_index=0, is_duplicate=False, diff_ratio=0.0))

        output = compositor.process(pairs, results)

        # Verify output shape
        assert output.frame.shape == (output_height, output_width, 3)

        # Verify output is not all zeros (something was rendered)
        assert output.frame.sum() > 0

        # Verify metrics
        assert output.metrics.frame_index == 0
        assert len(output.metrics.videos) == video_count

    @pytest.mark.parametrize("video_count", [2, 3, 4])
    def test_crop_mode_shows_center(self, qapp, video_count: int) -> None:
        """CROP mode shows center of source when cropping."""
        output_width = 1280
        output_height = 720

        # Source larger than slot - will be cropped
        source_width = 1280  # Full width
        source_height = 720

        compositor = SimpleCompositor(
            video_count=video_count,
            video_fps=[60.0] * video_count,
            output_width=output_width,
            output_height=output_height,
            scale_mode=ScaleMode.CROP,
        )

        slot_width = output_width // video_count

        # Create frames with distinct left/center/right colors
        pairs = []
        results = []
        for i in range(video_count):
            frame_data = np.zeros((source_height, source_width, 3), dtype=np.uint8)
            # Left third: red
            frame_data[:, :source_width // 3, 0] = 255
            # Center third: green
            frame_data[:, source_width // 3:2 * source_width // 3, 1] = 255
            # Right third: blue
            frame_data[:, 2 * source_width // 3:, 2] = 255

            view = FrameView(_data=frame_data, index=0, pts=0)
            pair = FramePair(prev=view, curr=view, _on_release=lambda: None)
            pairs.append(pair)
            results.append(FrameMetrics(frame_index=0, is_duplicate=False, diff_ratio=0.0))

        output = compositor.process(pairs, results)

        # Check center of first video slot - should be green (center of source)
        slot_center_x = slot_width // 2
        sample = output.frame[output_height // 2, slot_center_x, :]

        # Center should be predominantly green
        assert sample[1] > sample[0], "Center should show green (center of source)"
        assert sample[1] > sample[2], "Center should show green (center of source)"

    def test_crop_mode_centers_smaller_source(self, qapp) -> None:
        """CROP mode centers smaller source with black borders."""
        output_width = 1280
        output_height = 720
        source_width = 320
        source_height = 240

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[60.0],
            output_width=output_width,
            output_height=output_height,
            scale_mode=ScaleMode.CROP,
        )

        # Small white frame
        frame_data = np.full(
            (source_height, source_width, 3),
            fill_value=255,
            dtype=np.uint8,
        )
        view = FrameView(_data=frame_data, index=0, pts=0)
        pair = FramePair(prev=view, curr=view, _on_release=lambda: None)

        output = compositor.process([pair], [FrameMetrics(frame_index=0)])

        # Center should be white
        center_x = output_width // 2
        center_y = output_height // 2
        assert output.frame[center_y, center_x, 0] == 255

        # Corners should be black (border)
        assert output.frame[0, 0, 0] == 0
        assert output.frame[0, output_width - 1, 0] == 0
        assert output.frame[output_height - 1, 0, 0] == 0

    def test_fit_mode_preserves_aspect_ratio(self, qapp) -> None:
        """FIT mode preserves aspect ratio with letterboxing."""
        output_width = 1280
        output_height = 720

        # Wide source (16:9 into 16:9 slot - should fit perfectly)
        source_width = 1920
        source_height = 1080

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[60.0],
            output_width=output_width,
            output_height=output_height,
            scale_mode=ScaleMode.FIT,
        )

        # Solid color frame
        frame_data = np.full(
            (source_height, source_width, 3),
            fill_value=(100, 150, 200),
            dtype=np.uint8,
        )
        view = FrameView(_data=frame_data, index=0, pts=0)
        pair = FramePair(prev=view, curr=view, _on_release=lambda: None)

        output = compositor.process([pair], [FrameMetrics(frame_index=0)])

        # Center should have content
        center_x = output_width // 2
        center_y = output_height // 2
        assert output.frame[center_y, center_x, 0] > 0

    def test_stretch_mode_fills_slot(self, qapp) -> None:
        """STRETCH mode fills entire slot (ignoring aspect ratio)."""
        output_width = 1280
        output_height = 720
        source_width = 640
        source_height = 480

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[60.0],
            output_width=output_width,
            output_height=output_height,
            scale_mode=ScaleMode.STRETCH,
        )

        # Solid color frame
        frame_data = np.full(
            (source_height, source_width, 3),
            fill_value=(100, 150, 200),
            dtype=np.uint8,
        )
        view = FrameView(_data=frame_data, index=0, pts=0)
        pair = FramePair(prev=view, curr=view, _on_release=lambda: None)

        output = compositor.process([pair], [FrameMetrics(frame_index=0)])

        # All four corners should have content (not black)
        assert output.frame[0, 0, 0] > 0
        assert output.frame[0, output_width - 1, 0] > 0
        assert output.frame[output_height - 1, 0, 0] > 0
        assert output.frame[output_height - 1, output_width - 1, 0] > 0


class TestScalingModesWithExport:
    """Integration tests: scaling modes with full pipeline export."""

    @pytest.fixture(scope="class")
    def qapp(self):
        """Create QGuiApplication for QPainter operations."""
        app = QGuiApplication.instance()
        if app is None:
            app = QGuiApplication(sys.argv)
        return app

    @pytest.mark.parametrize(
        "scale_mode,video_count",
        list(itertools.product(
            [ScaleMode.CROP, ScaleMode.FIT, ScaleMode.STRETCH],
            [1, 2, 3, 4],
        )),
        ids=[
            f"{mode.name.lower()}_{count}vid"
            for mode, count in itertools.product(
                [ScaleMode.CROP, ScaleMode.FIT, ScaleMode.STRETCH],
                [1, 2, 3, 4],
            )
        ],
    )
    def test_export_all_combinations(
        self,
        qapp,
        tmp_path: Path,
        scale_mode: ScaleMode,
        video_count: int,
    ) -> None:
        """Export works for all scaling mode × video count combinations."""
        from trdrop.analysis.duplicate import DuplicateDetector
        from trdrop.compositor.simple import SimpleCompositor
        from trdrop.engine import StreamingEngine
        from trdrop.export import StreamingVideoExporter
        from trdrop.source.sequential import SequentialFrameSource
        from trdrop.video.reader import PyAVReader

        # Create very short test videos (0.5s each)
        video_paths = []
        for i in range(video_count):
            video_path = tmp_path / f"source_{i}.mp4"
            config = VideoConfig(
                container_fps=30,
                content_fps=15,
                duration_sec=0.5,
                width=320,
                height=240,
                pattern=PatternType.SOLID,
                seed=42 + i,
            )
            VideoGenerator(config).write(video_path)
            video_paths.append(video_path)

        # Create readers and sources
        readers = [PyAVReader(path) for path in video_paths]
        sources = [SequentialFrameSource(reader) for reader in readers]

        # Create compositor with specified scale mode
        compositor = SimpleCompositor(
            video_count=video_count,
            video_fps=[float(r.fps) for r in readers],
            output_width=640,
            output_height=360,
            scale_mode=scale_mode,
        )

        # Export
        output_path = tmp_path / f"output_{scale_mode.name}_{video_count}vid.mp4"
        exporter = StreamingVideoExporter(
            output_path,
            fps=readers[0].fps,
            codec="libx264",
            crf=23,
            preset="ultrafast",
        )

        engine = StreamingEngine(
            sources=sources,
            analyzers=[DuplicateDetector()],
            compositor=compositor,
            exporters=[exporter],
            synchronous=True,
        )

        engine.run()

        # Verify output exists and has content
        assert output_path.exists()
        assert output_path.stat().st_size > 0

        # Verify output is readable
        with PyAVReader(output_path) as output_reader:
            assert output_reader.total_frames > 0
            assert output_reader.width == 640
            assert output_reader.height == 360
