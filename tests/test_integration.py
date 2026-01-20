"""End-to-end integration tests for full analysis pipeline."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import pytest

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.engine.trdrop import TrdropEngine
from trdrop.export import export_csv, export_json, import_json
from trdrop.source.sequential import SequentialFrameSource
from trdrop.video.reader import PyAVReader


class TestEndToEndPipeline:
    """Full pipeline: generate video -> analyze -> export -> verify."""

    def test_full_pipeline_30fps_in_60fps(self) -> None:
        """Complete durchstich: 30fps content in 60fps container."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=1.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test_30in60.mp4"
            csv_path = Path(tmpdir) / "results.csv"
            json_path = Path(tmpdir) / "results.json"

            # Generate test video
            VideoGenerator(config).write(video_path)

            # Analyze
            reader = PyAVReader(video_path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])
            results = engine.run([(video_path, source)])

            assert len(results) == 1
            result = results[0]

            # Verify analysis results
            assert result.total_frames == 60
            assert result.unique_frames == 30
            assert result.duplicate_frames == 30
            assert result.detected_fps == pytest.approx(30.0, abs=1.0)

            # Export to CSV
            export_csv(result, csv_path)
            assert csv_path.exists()

            # Verify CSV content
            with csv_path.open() as f:
                lines = f.readlines()

            # Check summary comments
            assert any("# fps: 60" in line for line in lines)
            assert any("# detected_fps: 30" in line for line in lines)

            # Check data rows (skip comments and header)
            data_lines = [line for line in lines if not line.startswith("#")]
            reader_csv = csv.DictReader(data_lines)
            rows = list(reader_csv)
            assert len(rows) == 59  # 60 frames - 1 (first frame not compared)

            # Export to JSON
            export_json(results, json_path)
            assert json_path.exists()

            # Verify JSON roundtrip
            imported = import_json(json_path)
            assert len(imported) == 1
            imported_result = imported[0]

            assert imported_result.fps == result.fps
            assert imported_result.total_frames == result.total_frames
            assert imported_result.unique_frames == result.unique_frames
            assert imported_result.duplicate_frames == result.duplicate_frames
            assert len(imported_result.metrics) == len(result.metrics)

    def test_full_pipeline_native_60fps(self) -> None:
        """Native 60fps content should have no duplicates."""
        config = VideoConfig(
            container_fps=60,
            content_fps=60,
            duration_sec=1.0,
            pattern=PatternType.NOISE,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test_60fps.mp4"
            json_path = Path(tmpdir) / "results.json"

            VideoGenerator(config).write(video_path)

            reader = PyAVReader(video_path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])
            results = engine.run([(video_path, source)])

            result = results[0]
            assert result.duplicate_frames == 0
            assert result.detected_fps == pytest.approx(60.0, abs=1.0)

            # Export and roundtrip
            export_json(results, json_path)
            imported = import_json(json_path)

            assert imported[0].duplicate_frames == 0

    def test_multiple_videos_export(self) -> None:
        """Export multiple video results to single JSON."""
        configs = [
            VideoConfig(
                container_fps=60, content_fps=60,
                duration_sec=0.5, pattern=PatternType.COUNTER,
            ),
            VideoConfig(
                container_fps=60, content_fps=30,
                duration_sec=0.5, pattern=PatternType.COUNTER,
            ),
            VideoConfig(
                container_fps=60, content_fps=20,
                duration_sec=0.5, pattern=PatternType.COUNTER,
            ),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            sources = []
            for i, config in enumerate(configs):
                path = Path(tmpdir) / f"video_{i}.mp4"
                VideoGenerator(config).write(path)
                reader = PyAVReader(path)
                source = SequentialFrameSource(reader)
                sources.append((path, source))

            engine = TrdropEngine([DuplicateDetector()], video_workers=2)
            results = engine.run(sources)

            assert len(results) == 3

            # Export all to JSON
            json_path = Path(tmpdir) / "all_results.json"
            export_json(results, json_path)

            # Roundtrip
            imported = import_json(json_path)
            assert len(imported) == 3

            # Verify each result preserved
            for orig, imp in zip(results, imported):
                assert imp.total_frames == orig.total_frames
                assert imp.unique_frames == orig.unique_frames
                assert imp.duplicate_frames == orig.duplicate_frames


class TestCSVExport:
    """Tests specific to CSV export functionality."""

    def test_csv_without_summary(self) -> None:
        """CSV export without summary comments."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=0.5,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test.mp4"
            csv_path = Path(tmpdir) / "results.csv"

            VideoGenerator(config).write(video_path)

            reader = PyAVReader(video_path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])
            results = engine.run([(video_path, source)])

            export_csv(results[0], csv_path, include_summary=False)

            with csv_path.open() as f:
                lines = f.readlines()

            # No comment lines
            assert not any(line.startswith("#") for line in lines)
            # First line is header
            assert lines[0].strip() == "frame_index,is_duplicate,diff_ratio,tear_rows"

    def test_csv_diff_ratio_precision(self) -> None:
        """CSV diff_ratio should have sufficient precision."""
        config = VideoConfig(
            container_fps=60,
            content_fps=60,
            duration_sec=0.5,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test.mp4"
            csv_path = Path(tmpdir) / "results.csv"

            VideoGenerator(config).write(video_path)

            reader = PyAVReader(video_path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])
            results = engine.run([(video_path, source)])

            export_csv(results[0], csv_path)

            with csv_path.open() as f:
                reader_csv = csv.DictReader(
                    [line for line in f.readlines() if not line.startswith("#")]
                )
                rows = list(reader_csv)

            # Check that diff_ratio has decimal places
            for row in rows:
                if row["diff_ratio"]:
                    assert "." in row["diff_ratio"]
                    # 6 decimal places
                    parts = row["diff_ratio"].split(".")
                    assert len(parts[1]) == 6


class TestJSONExport:
    """Tests specific to JSON export functionality."""

    def test_json_version_check(self) -> None:
        """Import should reject unsupported versions."""
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "bad_version.json"

            with json_path.open("w") as f:
                json.dump({"version": 999, "videos": []}, f)

            with pytest.raises(ValueError, match=r"Unsupported JSON format version"):
                import_json(json_path)

    def test_json_metrics_roundtrip_with_all_fields(self) -> None:
        """All FrameMetrics fields should survive roundtrip."""
        from trdrop.engine.trdrop import VideoResult
        from trdrop.types.metrics import FrameMetrics

        # Create result with all fields populated
        metrics = (
            FrameMetrics(
                frame_index=1,
                is_duplicate=True,
                diff_ratio=0.001234,
                tear_rows=(100, 200, 300),
                frame_time_ms=16.67,
            ),
            FrameMetrics(
                frame_index=2,
                is_duplicate=False,
                diff_ratio=0.567890,
            ),
        )

        result = VideoResult(
            path=Path("test.mp4"),
            fps=60.0,
            total_frames=3,
            metrics=metrics,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "roundtrip.json"

            export_json([result], json_path)
            imported = import_json(json_path)

            imp_result = imported[0]
            imp_metrics = imp_result.metrics

            # Check all fields preserved
            assert imp_metrics[0].frame_index == 1
            assert imp_metrics[0].is_duplicate is True
            assert imp_metrics[0].diff_ratio == pytest.approx(0.001234)
            assert imp_metrics[0].tear_rows == (100, 200, 300)
            assert imp_metrics[0].frame_time_ms == pytest.approx(16.67)

            assert imp_metrics[1].frame_index == 2
            assert imp_metrics[1].is_duplicate is False
            assert imp_metrics[1].tear_rows is None
            assert imp_metrics[1].frame_time_ms is None

    def test_json_compact_format(self) -> None:
        """JSON export with indent=None should be compact."""
        from trdrop.engine.trdrop import VideoResult
        from trdrop.types.metrics import FrameMetrics

        result = VideoResult(
            path=Path("test.mp4"),
            fps=60.0,
            total_frames=2,
            metrics=(FrameMetrics(frame_index=1, is_duplicate=False),),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "compact.json"

            export_json([result], json_path, indent=None)

            with json_path.open() as f:
                content = f.read()

            # Compact format should be single line
            assert "\n" not in content.strip()


class TestExportEdgeCases:
    """Edge cases and error handling for exports."""

    def test_empty_results_json(self) -> None:
        """Exporting empty results list should work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "empty.json"

            export_json([], json_path)
            imported = import_json(json_path)

            assert imported == []

    def test_video_with_no_metrics(self) -> None:
        """Video with empty metrics tuple should export."""
        from trdrop.engine.trdrop import VideoResult

        result = VideoResult(
            path=Path("empty.mp4"),
            fps=30.0,
            total_frames=1,
            metrics=(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "empty.csv"
            json_path = Path(tmpdir) / "empty.json"

            export_csv(result, csv_path)
            export_json([result], json_path)

            # Both should create valid files
            assert csv_path.exists()
            assert json_path.exists()

            # JSON roundtrip should work
            imported = import_json(json_path)
            assert len(imported) == 1
            assert imported[0].metrics == ()
