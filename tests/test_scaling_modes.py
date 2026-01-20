"""Tests for scaling modes across different video count configurations.

Tests all combinations of:
- Scale modes: CROP, FIT, STRETCH
- Video counts: 1, 2, 3, 4 (layouts: 1:1:1:1, 1:1:1, 1:1, single)

CROP mode tests run by default. FIT/STRETCH require --run-slow flag:
    uv run pytest tests/test_scaling_modes.py --run-slow
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from PyQt6.QtGui import QGuiApplication

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.compositor import ScaleMode, SimpleCompositor
from trdrop.types.frames import FramePair, FrameView
from trdrop.types.metrics import FrameMetrics


class TestScalingModesCROP:
    """Test CROP mode behavior - runs by default."""

    @pytest.fixture(scope="class")
    def qapp(self):
        """Create QGuiApplication for QPainter operations."""
        app = QGuiApplication.instance()
        if app is None:
            app = QGuiApplication(sys.argv)
        return app

    @pytest.mark.parametrize("video_count", [1, 2, 3, 4])
    def test_crop_produces_valid_output(self, qapp, video_count: int) -> None:
        """CROP compositor produces correctly sized output."""
        output_width = 1280
        output_height = 720
        source_width = 640
        source_height = 480

        compositor = SimpleCompositor(
            video_count=video_count,
            video_fps=[60.0] * video_count,
            output_width=output_width,
            output_height=output_height,
            scale_mode=ScaleMode.CROP,
        )

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

        assert output.frame.shape == (output_height, output_width, 3)
        assert output.frame.sum() > 0
        assert len(output.metrics.videos) == video_count

    @pytest.mark.parametrize("video_count", [2, 3, 4])
    def test_crop_shows_center(self, qapp, video_count: int) -> None:
        """CROP mode shows center of source when cropping."""
        output_width = 1280
        output_height = 720
        source_width = 1280
        source_height = 720

        compositor = SimpleCompositor(
            video_count=video_count,
            video_fps=[60.0] * video_count,
            output_width=output_width,
            output_height=output_height,
            scale_mode=ScaleMode.CROP,
        )

        slot_width = output_width // video_count

        pairs = []
        results = []
        for i in range(video_count):
            frame_data = np.zeros((source_height, source_width, 3), dtype=np.uint8)
            frame_data[:, :source_width // 3, 0] = 255  # Left: red
            frame_data[:, source_width // 3:2 * source_width // 3, 1] = 255  # Center: green
            frame_data[:, 2 * source_width // 3:, 2] = 255  # Right: blue

            view = FrameView(_data=frame_data, index=0, pts=0)
            pair = FramePair(prev=view, curr=view, _on_release=lambda: None)
            pairs.append(pair)
            results.append(FrameMetrics(frame_index=0, is_duplicate=False, diff_ratio=0.0))

        output = compositor.process(pairs, results)

        slot_center_x = slot_width // 2
        sample = output.frame[output_height // 2, slot_center_x, :]
        assert sample[1] > sample[0], "Center should show green"
        assert sample[1] > sample[2], "Center should show green"

    def test_crop_centers_smaller_source(self, qapp) -> None:
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

        frame_data = np.full((source_height, source_width, 3), 255, dtype=np.uint8)
        view = FrameView(_data=frame_data, index=0, pts=0)
        pair = FramePair(prev=view, curr=view, _on_release=lambda: None)

        output = compositor.process([pair], [FrameMetrics(frame_index=0)])

        center_x = output_width // 2
        center_y = output_height // 2
        assert output.frame[center_y, center_x, 0] == 255  # Center white
        assert output.frame[0, 0, 0] == 0  # Corner black

    @pytest.mark.parametrize("video_count", [1, 2, 3, 4])
    def test_crop_export_integration(self, qapp, tmp_path: Path, video_count: int) -> None:
        """CROP mode exports correctly for all video counts."""
        from trdrop.analysis.duplicate import DuplicateDetector
        from trdrop.engine import StreamingEngine
        from trdrop.export import StreamingVideoExporter
        from trdrop.source.sequential import SequentialFrameSource
        from trdrop.video.reader import PyAVReader

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

        readers = [PyAVReader(path) for path in video_paths]
        sources = [SequentialFrameSource(reader) for reader in readers]

        compositor = SimpleCompositor(
            video_count=video_count,
            video_fps=[float(r.fps) for r in readers],
            output_width=640,
            output_height=360,
            scale_mode=ScaleMode.CROP,
        )

        output_path = tmp_path / f"output_crop_{video_count}vid.mp4"
        exporter = StreamingVideoExporter(
            output_path, fps=readers[0].fps, codec="libx264", crf=23, preset="ultrafast"
        )

        engine = StreamingEngine(
            sources=sources,
            analyzers=[DuplicateDetector()],
            compositor=compositor,
            exporters=[exporter],
            synchronous=True,
        )
        engine.run()

        assert output_path.exists()
        with PyAVReader(output_path) as reader:
            assert reader.total_frames > 0


@pytest.mark.slow
class TestScalingModesFitStretch:
    """Test FIT/STRETCH modes - requires --run-slow flag."""

    @pytest.fixture(scope="class")
    def qapp(self):
        app = QGuiApplication.instance()
        if app is None:
            app = QGuiApplication(sys.argv)
        return app

    @pytest.mark.parametrize(
        "scale_mode", [ScaleMode.FIT, ScaleMode.STRETCH], ids=["fit", "stretch"]
    )
    @pytest.mark.parametrize("video_count", [1, 2, 3, 4])
    def test_produces_valid_output(self, qapp, scale_mode: ScaleMode, video_count: int) -> None:
        """FIT/STRETCH modes produce correctly sized output."""
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
        assert output.frame.shape == (output_height, output_width, 3)
        assert output.frame.sum() > 0

    def test_fit_preserves_aspect_ratio(self, qapp) -> None:
        """FIT mode preserves aspect ratio with letterboxing."""
        output_width = 1280
        output_height = 720
        source_width = 1920
        source_height = 1080

        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[60.0],
            output_width=output_width,
            output_height=output_height,
            scale_mode=ScaleMode.FIT,
        )

        frame_data = np.full((source_height, source_width, 3), (100, 150, 200), dtype=np.uint8)
        view = FrameView(_data=frame_data, index=0, pts=0)
        pair = FramePair(prev=view, curr=view, _on_release=lambda: None)

        output = compositor.process([pair], [FrameMetrics(frame_index=0)])
        assert output.frame[output_height // 2, output_width // 2, 0] > 0

    def test_stretch_fills_slot(self, qapp) -> None:
        """STRETCH mode fills entire slot."""
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

        frame_data = np.full((source_height, source_width, 3), (100, 150, 200), dtype=np.uint8)
        view = FrameView(_data=frame_data, index=0, pts=0)
        pair = FramePair(prev=view, curr=view, _on_release=lambda: None)

        output = compositor.process([pair], [FrameMetrics(frame_index=0)])

        # All corners should have content
        assert output.frame[0, 0, 0] > 0
        assert output.frame[0, output_width - 1, 0] > 0
        assert output.frame[output_height - 1, 0, 0] > 0
        assert output.frame[output_height - 1, output_width - 1, 0] > 0

    @pytest.mark.parametrize(
        "scale_mode", [ScaleMode.FIT, ScaleMode.STRETCH], ids=["fit", "stretch"]
    )
    @pytest.mark.parametrize("video_count", [1, 2, 3, 4])
    def test_export_integration(
        self, qapp, tmp_path: Path, scale_mode: ScaleMode, video_count: int
    ) -> None:
        """FIT/STRETCH export for all video counts."""
        from trdrop.analysis.duplicate import DuplicateDetector
        from trdrop.engine import StreamingEngine
        from trdrop.export import StreamingVideoExporter
        from trdrop.source.sequential import SequentialFrameSource
        from trdrop.video.reader import PyAVReader

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

        readers = [PyAVReader(path) for path in video_paths]
        sources = [SequentialFrameSource(reader) for reader in readers]

        compositor = SimpleCompositor(
            video_count=video_count,
            video_fps=[float(r.fps) for r in readers],
            output_width=640,
            output_height=360,
            scale_mode=scale_mode,
        )

        output_path = tmp_path / f"output_{scale_mode.name}_{video_count}vid.mp4"
        exporter = StreamingVideoExporter(
            output_path, fps=readers[0].fps, codec="libx264", crf=23, preset="ultrafast"
        )

        engine = StreamingEngine(
            sources=sources,
            analyzers=[DuplicateDetector()],
            compositor=compositor,
            exporters=[exporter],
            synchronous=True,
        )
        engine.run()

        assert output_path.exists()
        with PyAVReader(output_path) as reader:
            assert reader.total_frames > 0
