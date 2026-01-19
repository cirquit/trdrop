"""End-to-end tests for TrdropEngine."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.engine.trdrop import TrdropEngine, VideoResult
from trdrop.source.sequential import SequentialFrameSource
from trdrop.video.reader import PyAVReader


class TestTrdropEngine:
    """End-to-end tests for the TrdropEngine."""

    def test_detects_60fps_native(self) -> None:
        """60fps content in 60fps container should have no duplicates."""
        config = VideoConfig(
            container_fps=60,
            content_fps=60,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "60fps.mp4"
            VideoGenerator(config).write(path)

            reader = PyAVReader(path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])

            results = engine.run([(path, source)])

            assert len(results) == 1
            result = results[0]
            assert result.total_frames == 120
            assert result.fps == pytest.approx(60.0, abs=0.1)
            assert result.detected_fps == pytest.approx(60.0, abs=2.0)
            assert result.duplicate_frames == 0

    def test_detects_30fps_in_60fps_container(self) -> None:
        """30fps content in 60fps container should have 50% duplicates."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "30fps.mp4"
            VideoGenerator(config).write(path)

            reader = PyAVReader(path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])

            results = engine.run([(path, source)])

            result = results[0]
            assert result.total_frames == 120
            assert result.unique_frames == 60
            assert result.duplicate_frames == 60
            assert result.detected_fps == pytest.approx(30.0, abs=1.0)

    def test_detects_24fps_in_60fps_container(self) -> None:
        """24fps content in 60fps container (common for film)."""
        config = VideoConfig(
            container_fps=60,
            content_fps=24,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "24fps.mp4"
            VideoGenerator(config).write(path)

            reader = PyAVReader(path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])

            results = engine.run([(path, source)])

            result = results[0]
            assert result.total_frames == 120
            assert result.unique_frames == 48
            assert result.duplicate_frames == 72
            assert result.detected_fps == pytest.approx(24.0, abs=1.0)

    def test_detects_15fps_in_60fps_container(self) -> None:
        """15fps content in 60fps container (low framerate)."""
        config = VideoConfig(
            container_fps=60,
            content_fps=15,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "15fps.mp4"
            VideoGenerator(config).write(path)

            reader = PyAVReader(path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])

            results = engine.run([(path, source)])

            result = results[0]
            assert result.total_frames == 120
            assert result.unique_frames == 30
            assert result.duplicate_frames == 90
            assert result.detected_fps == pytest.approx(15.0, abs=1.0)

    def test_duration_calculated_correctly(self) -> None:
        """Duration should match expected value."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=3.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "3sec.mp4"
            VideoGenerator(config).write(path)

            reader = PyAVReader(path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])

            results = engine.run([(path, source)])

            result = results[0]
            assert result.duration_sec == pytest.approx(3.0, abs=0.1)
            assert result.total_frames == 180

    @pytest.mark.parametrize("content_fps", [20, 25, 30, 40, 50])
    def test_various_framerates(self, content_fps: int) -> None:
        """Various content framerates should be detected correctly."""
        config = VideoConfig(
            container_fps=60,
            content_fps=content_fps,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / f"{content_fps}fps.mp4"
            VideoGenerator(config).write(path)

            reader = PyAVReader(path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])

            results = engine.run([(path, source)])

            result = results[0]
            assert result.detected_fps == pytest.approx(
                float(content_fps), abs=2.0
            ), f"Expected {content_fps} fps, got {result.detected_fps:.1f}"


class TestTrdropEngineMultipleVideos:
    """Test engine with multiple videos."""

    def test_processes_multiple_videos(self) -> None:
        """Engine should process multiple videos in parallel."""
        configs = [
            VideoConfig(
                container_fps=60, content_fps=60, duration_sec=1.0, pattern=PatternType.COUNTER
            ),
            VideoConfig(
                container_fps=60, content_fps=30, duration_sec=1.0, pattern=PatternType.COUNTER
            ),
            VideoConfig(
                container_fps=60, content_fps=24, duration_sec=1.0, pattern=PatternType.COUNTER
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
            assert results[0].detected_fps == pytest.approx(60.0, abs=2.0)
            assert results[1].detected_fps == pytest.approx(30.0, abs=2.0)
            assert results[2].detected_fps == pytest.approx(24.0, abs=2.0)


class TestTrdropEngineWithPatterns:
    """Test engine with different visual patterns."""

    @pytest.mark.parametrize("pattern", [
        PatternType.COUNTER,
        PatternType.NOISE,
        PatternType.BLOCKS,
    ])
    def test_pattern_detection(self, pattern: PatternType) -> None:
        """Different patterns should all detect 30fps correctly."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=1.0,
            pattern=pattern,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / f"{pattern.value}.mp4"
            VideoGenerator(config).write(path)

            reader = PyAVReader(path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])

            results = engine.run([(path, source)])

            result = results[0]
            assert result.detected_fps == pytest.approx(30.0, abs=2.0), (
                f"Pattern {pattern.value} detected {result.detected_fps:.1f} fps"
            )


class TestEngineReleaseContract:
    """Tests for engine's frame release contract."""

    def test_engine_releases_frames_no_warnings(self) -> None:
        """Engine should call release() on all frame pairs without warnings."""
        import warnings

        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=1.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.mp4"
            VideoGenerator(config).write(path)

            reader = PyAVReader(path)
            source = SequentialFrameSource(reader)
            engine = TrdropEngine([DuplicateDetector()])

            # Should complete without any RuntimeWarnings about unreleased pairs
            with warnings.catch_warnings():
                warnings.simplefilter("error", RuntimeWarning)
                results = engine.run([(path, source)])

            assert len(results) == 1
            assert results[0].total_frames == 60


class TestVideoResult:
    """Tests for VideoResult dataclass."""

    def test_result_fields(self) -> None:
        """VideoResult should have all expected fields."""
        from trdrop.types.metrics import FrameMetrics

        metrics = tuple(
            FrameMetrics(
                frame_index=i,
                is_duplicate=(i % 2 == 0),
                diff_ratio=0.0 if i % 2 == 0 else 0.5,
            )
            for i in range(1, 120)
        )

        result = VideoResult(
            path=Path("test.mp4"),
            fps=60.0,
            total_frames=120,
            metrics=metrics,
        )

        assert result.path == Path("test.mp4")
        assert result.fps == 60.0
        assert result.total_frames == 120
        assert result.duration_sec == 2.0

    def test_result_consistency(self) -> None:
        """unique + duplicate should equal total - 1 (first frame not compared)."""
        from trdrop.types.metrics import FrameMetrics

        metrics = tuple(
            FrameMetrics(frame_index=i, is_duplicate=(i % 2 == 0), diff_ratio=0.0)
            for i in range(1, 120)
        )

        result = VideoResult(
            path=Path("test.mp4"),
            fps=60.0,
            total_frames=120,
            metrics=metrics,
        )

        # unique_frames includes first frame + non-duplicates from metrics
        # duplicate_frames is count of duplicates from metrics
        assert result.unique_frames + result.duplicate_frames == result.total_frames
