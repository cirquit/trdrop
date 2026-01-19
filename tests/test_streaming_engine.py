"""Tests for StreamingEngine with compositor and exporters."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import pytest

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.compositor import SimpleCompositor
from trdrop.engine import StreamingEngine
from trdrop.export import StreamingCSVExporter, StreamingVideoExporter
from trdrop.source.sequential import SequentialFrameSource
from trdrop.video.reader import PyAVReader


class TestStreamingEngine:
    """Tests for streaming engine pipeline."""

    def test_single_video_with_csv_export(self) -> None:
        """Single video analysis with CSV export."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=1.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test.mp4"
            csv_path = Path(tmpdir) / "metrics.csv"

            VideoGenerator(config).write(video_path)

            reader = PyAVReader(video_path)
            source = SequentialFrameSource(reader)

            compositor = SimpleCompositor(
                video_count=1,
                video_fps=[60.0],
                output_width=640,
                output_height=480,
            )

            csv_exporter = StreamingCSVExporter(csv_path)

            engine = StreamingEngine(
                sources=[source],
                analyzers=[DuplicateDetector()],
                compositor=compositor,
                exporters=[csv_exporter],
            )

            engine.run()

            # Verify CSV output
            assert csv_path.exists()

            with csv_path.open() as f:
                reader_csv = csv.DictReader(f)
                rows = list(reader_csv)

            # 60 frames - 1 = 59 frame pairs
            assert len(rows) == 59

            # Check windowed_fps converges toward 30
            last_row = rows[-1]
            windowed_fps = float(last_row["windowed_fps"])
            assert 25 < windowed_fps < 35, f"Expected ~30 fps, got {windowed_fps}"

    def test_single_video_with_video_export(self) -> None:
        """Single video analysis with video export."""
        config = VideoConfig(
            container_fps=60,
            content_fps=60,
            duration_sec=0.5,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test.mp4"
            output_path = Path(tmpdir) / "output.mp4"

            VideoGenerator(config).write(video_path)

            reader = PyAVReader(video_path)
            source = SequentialFrameSource(reader)

            compositor = SimpleCompositor(
                video_count=1,
                video_fps=[60.0],
                output_width=320,
                output_height=240,
            )

            video_exporter = StreamingVideoExporter(
                output_path, fps=60.0, crf=28, preset="ultrafast"
            )

            engine = StreamingEngine(
                sources=[source],
                analyzers=[DuplicateDetector()],
                compositor=compositor,
                exporters=[video_exporter],
            )

            engine.run()

            # Verify output video exists and is readable
            assert output_path.exists()

            output_reader = PyAVReader(output_path)
            assert output_reader.width == 320
            assert output_reader.height == 240
            # Frame count may differ slightly due to encoding
            assert output_reader.total_frames >= 25
            output_reader.close()

    def test_multiple_videos_lockstep(self) -> None:
        """Multiple videos processed in lockstep."""
        config1 = VideoConfig(
            container_fps=60,
            content_fps=60,
            duration_sec=0.5,
            pattern=PatternType.COUNTER,
        )
        config2 = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=0.5,
            pattern=PatternType.NOISE,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            video1_path = Path(tmpdir) / "video1.mp4"
            video2_path = Path(tmpdir) / "video2.mp4"
            csv_path = Path(tmpdir) / "metrics.csv"

            VideoGenerator(config1).write(video1_path)
            VideoGenerator(config2).write(video2_path)

            reader1 = PyAVReader(video1_path)
            reader2 = PyAVReader(video2_path)
            source1 = SequentialFrameSource(reader1)
            source2 = SequentialFrameSource(reader2)

            compositor = SimpleCompositor(
                video_count=2,
                video_fps=[60.0, 60.0],
                output_width=640,
                output_height=240,
            )

            csv_exporter = StreamingCSVExporter(csv_path)

            engine = StreamingEngine(
                sources=[source1, source2],
                analyzers=[DuplicateDetector()],
                compositor=compositor,
                exporters=[csv_exporter],
            )

            engine.run()

            # Verify CSV has rows for both videos
            with csv_path.open() as f:
                reader_csv = csv.DictReader(f)
                rows = list(reader_csv)

            # Each frame produces 2 rows (one per video)
            # 30 frames - 1 = 29 pairs, 29 * 2 = 58 rows
            assert len(rows) == 58

            # Check both videos present
            video_indices = {row["video_index"] for row in rows}
            assert video_indices == {"0", "1"}

    def test_progress_callback(self) -> None:
        """Progress callback is invoked."""
        config = VideoConfig(
            container_fps=60,
            content_fps=60,
            duration_sec=0.5,
            pattern=PatternType.COUNTER,
        )

        progress_calls: list[tuple[int, int]] = []

        def on_progress(frame_idx: int, total: int) -> None:
            progress_calls.append((frame_idx, total))

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test.mp4"
            VideoGenerator(config).write(video_path)

            reader = PyAVReader(video_path)
            source = SequentialFrameSource(reader)

            compositor = SimpleCompositor(
                video_count=1,
                video_fps=[60.0],
                output_width=320,
                output_height=240,
            )

            engine = StreamingEngine(
                sources=[source],
                analyzers=[DuplicateDetector()],
                compositor=compositor,
                exporters=[],
                on_frame=on_progress,
            )

            engine.run()

            # Should have been called for each frame pair
            assert len(progress_calls) == 29  # 30 frames - 1


class TestStreamingEngineEdgeCases:
    """Edge cases for streaming engine."""

    def test_no_exporters(self) -> None:
        """Engine runs without exporters (analysis only)."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=0.5,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test.mp4"
            VideoGenerator(config).write(video_path)

            reader = PyAVReader(video_path)
            source = SequentialFrameSource(reader)

            compositor = SimpleCompositor(
                video_count=1,
                video_fps=[60.0],
                output_width=320,
                output_height=240,
            )

            engine = StreamingEngine(
                sources=[source],
                analyzers=[DuplicateDetector()],
                compositor=compositor,
                exporters=[],  # No exporters
            )

            # Should complete without error
            engine.run()

    def test_multiple_exporters(self) -> None:
        """Multiple exporters receive same data."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=0.5,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test.mp4"
            csv1_path = Path(tmpdir) / "metrics1.csv"
            csv2_path = Path(tmpdir) / "metrics2.csv"

            VideoGenerator(config).write(video_path)

            reader = PyAVReader(video_path)
            source = SequentialFrameSource(reader)

            compositor = SimpleCompositor(
                video_count=1,
                video_fps=[60.0],
                output_width=320,
                output_height=240,
            )

            engine = StreamingEngine(
                sources=[source],
                analyzers=[DuplicateDetector()],
                compositor=compositor,
                exporters=[
                    StreamingCSVExporter(csv1_path),
                    StreamingCSVExporter(csv2_path),
                ],
            )

            engine.run()

            # Both files should be identical
            with csv1_path.open() as f1, csv2_path.open() as f2:
                content1 = f1.read()
                content2 = f2.read()

            assert content1 == content2

    def test_empty_sources_raises(self) -> None:
        """Empty sources list raises ValueError."""
        compositor = SimpleCompositor(
            video_count=1,
            video_fps=[60.0],
            output_width=320,
            output_height=240,
        )

        with pytest.raises(ValueError, match="At least one source required"):
            StreamingEngine(
                sources=[],
                analyzers=[DuplicateDetector()],
                compositor=compositor,
                exporters=[],
            )
