"""Integration tests for FPS detection accuracy.

These tests verify that the NumpyAnalyzer correctly detects real FPS
by generating test videos with known properties and checking detection accuracy.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import av
import pytest

from tests.testkit import PatternType, VideoConfig, VideoGenerator
from trdrop.analysis.core import NumpyAnalyzer


class TestFPSDetectionRawFrames:
    """Test FPS detection on raw generated frames (no encoding)."""

    @pytest.fixture
    def analyzer(self) -> NumpyAnalyzer:
        return NumpyAnalyzer(pixel_threshold=10, duplicate_threshold=0.01)

    def _detect_fps(
        self,
        config: VideoConfig,
        analyzer: NumpyAnalyzer,
    ) -> tuple[int, int, float]:
        """
        Detect FPS from generated frames.

        Returns:
            (unique_count, duplicate_count, detected_fps)
        """
        gen = VideoGenerator(config)
        resolved = config.resolve()

        prev = None
        duplicates = 0
        uniques = 0

        for frame in gen.iter_frames():
            curr = frame.array.copy()  # Must copy - generator reuses arrays
            if prev is not None:
                is_dup, _ = analyzer.compare(prev, curr)
                if is_dup:
                    duplicates += 1
                else:
                    uniques += 1
            prev = curr

        # First frame is always unique
        uniques += 1
        detected_fps = uniques / resolved.duration_sec

        return uniques, duplicates, detected_fps

    def test_60fps_native_no_duplicates(self, analyzer: NumpyAnalyzer) -> None:
        """60fps content in 60fps container should have no duplicates."""
        config = VideoConfig(
            container_fps=60,
            content_fps=60,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        uniques, duplicates, detected_fps = self._detect_fps(config, analyzer)

        assert uniques == 120
        assert duplicates == 0
        assert detected_fps == pytest.approx(60.0, abs=0.1)

    def test_30fps_in_60fps_container(self, analyzer: NumpyAnalyzer) -> None:
        """30fps content in 60fps container should have 50% duplicates."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        uniques, duplicates, detected_fps = self._detect_fps(config, analyzer)

        assert uniques == 60
        assert duplicates == 60
        assert detected_fps == pytest.approx(30.0, abs=0.1)

    def test_24fps_in_60fps_container(self, analyzer: NumpyAnalyzer) -> None:
        """24fps content in 60fps container (common for film content)."""
        config = VideoConfig(
            container_fps=60,
            content_fps=24,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        uniques, duplicates, detected_fps = self._detect_fps(config, analyzer)

        assert uniques == 48
        assert duplicates == 72
        assert detected_fps == pytest.approx(24.0, abs=0.1)

    def test_45fps_in_60fps_container(self, analyzer: NumpyAnalyzer) -> None:
        """45fps content in 60fps container (variable framerate scenario)."""
        config = VideoConfig(
            container_fps=60,
            content_fps=45,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        uniques, duplicates, detected_fps = self._detect_fps(config, analyzer)

        assert uniques == 90
        assert duplicates == 30
        assert detected_fps == pytest.approx(45.0, abs=0.1)

    def test_15fps_in_60fps_container(self, analyzer: NumpyAnalyzer) -> None:
        """15fps content in 60fps container (low framerate scenario)."""
        config = VideoConfig(
            container_fps=60,
            content_fps=15,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        uniques, duplicates, detected_fps = self._detect_fps(config, analyzer)

        assert uniques == 30
        assert duplicates == 90
        assert detected_fps == pytest.approx(15.0, abs=0.1)

    @pytest.mark.parametrize("pattern", [
        PatternType.COUNTER,
        PatternType.NOISE,
        PatternType.SOLID,
        PatternType.BLOCKS,
    ])
    def test_multiple_patterns_detect_correctly(
        self,
        analyzer: NumpyAnalyzer,
        pattern: PatternType,
    ) -> None:
        """Various patterns should all detect 30fps correctly."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=1.0,
            pattern=pattern,
        )

        uniques, duplicates, detected_fps = self._detect_fps(config, analyzer)

        # Allow some tolerance for patterns with subtle differences
        assert detected_fps == pytest.approx(30.0, abs=2.0), (
            f"Pattern {pattern.value} detected {detected_fps:.1f} fps, expected 30"
        )


class TestFPSDetectionEncodedVideo:
    """Test FPS detection on H.264 encoded videos.

    These tests verify that detection works correctly even after
    lossy compression, which can introduce subtle frame differences.
    """

    @pytest.fixture
    def analyzer(self) -> NumpyAnalyzer:
        return NumpyAnalyzer(pixel_threshold=10, duplicate_threshold=0.01)

    def _detect_fps_from_file(
        self,
        video_path: Path,
        analyzer: NumpyAnalyzer,
        duration_sec: float,
    ) -> tuple[int, int, float]:
        """
        Detect FPS from an encoded video file.

        Returns:
            (unique_count, duplicate_count, detected_fps)
        """
        with av.open(str(video_path)) as container:
            stream = container.streams.video[0]

            prev = None
            duplicates = 0
            uniques = 0

            for frame in container.decode(stream):
                curr = frame.to_ndarray(format="rgb24")
                if prev is not None:
                    is_dup, _ = analyzer.compare(prev, curr)
                    if is_dup:
                        duplicates += 1
                    else:
                        uniques += 1
                prev = curr.copy()

            uniques += 1  # First frame
            detected_fps = uniques / duration_sec

            return uniques, duplicates, detected_fps

    def test_encoded_30fps_detection(self, analyzer: NumpyAnalyzer) -> None:
        """30fps encoded video should be detected correctly."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_30fps.mp4"
            gen = VideoGenerator(config)
            gen.write(path)

            uniques, duplicates, detected_fps = self._detect_fps_from_file(
                path, analyzer, 2.0
            )

            assert detected_fps == pytest.approx(30.0, abs=1.0), (
                f"Encoded video detected {detected_fps:.1f} fps, expected 30"
            )

    def test_encoded_24fps_detection(self, analyzer: NumpyAnalyzer) -> None:
        """24fps encoded video should be detected correctly."""
        config = VideoConfig(
            container_fps=60,
            content_fps=24,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_24fps.mp4"
            gen = VideoGenerator(config)
            gen.write(path)

            uniques, duplicates, detected_fps = self._detect_fps_from_file(
                path, analyzer, 2.0
            )

            assert detected_fps == pytest.approx(24.0, abs=1.0), (
                f"Encoded video detected {detected_fps:.1f} fps, expected 24"
            )

    def test_encoded_60fps_native(self, analyzer: NumpyAnalyzer) -> None:
        """60fps native encoded video should have no false duplicates."""
        config = VideoConfig(
            container_fps=60,
            content_fps=60,
            duration_sec=2.0,
            pattern=PatternType.COUNTER,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_60fps.mp4"
            gen = VideoGenerator(config)
            gen.write(path)

            uniques, duplicates, detected_fps = self._detect_fps_from_file(
                path, analyzer, 2.0
            )

            # Allow small tolerance for encoding artifacts
            assert detected_fps == pytest.approx(60.0, abs=2.0), (
                f"Encoded video detected {detected_fps:.1f} fps, expected 60"
            )


class TestAnalyzerAccuracy:
    """Test analyzer accuracy against ground truth."""

    @pytest.fixture
    def analyzer(self) -> NumpyAnalyzer:
        return NumpyAnalyzer(pixel_threshold=10, duplicate_threshold=0.01)

    def test_per_frame_accuracy(self, analyzer: NumpyAnalyzer) -> None:
        """Each frame's duplicate status should match ground truth."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=1.0,
            pattern=PatternType.COUNTER,
        )
        gen = VideoGenerator(config)

        prev = None
        mismatches = []

        for frame in gen.iter_frames():
            curr = frame.array.copy()
            if prev is not None:
                detected_dup, diff = analyzer.compare(prev, curr)
                expected_dup = frame.is_duplicate

                if detected_dup != expected_dup:
                    mismatches.append({
                        "frame": frame.index,
                        "expected": expected_dup,
                        "detected": detected_dup,
                        "diff": diff,
                    })
            prev = curr

        assert len(mismatches) == 0, (
            f"Frame detection mismatches: {mismatches[:5]}"
            + (f" ... and {len(mismatches) - 5} more" if len(mismatches) > 5 else "")
        )

    def test_diff_ratio_for_duplicates_is_zero(
        self,
        analyzer: NumpyAnalyzer,
    ) -> None:
        """Duplicate frames should have diff_ratio of exactly 0.0."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=1.0,
            pattern=PatternType.COUNTER,
        )
        gen = VideoGenerator(config)

        prev = None
        for frame in gen.iter_frames():
            curr = frame.array.copy()
            if prev is not None and frame.is_duplicate:
                _, diff = analyzer.compare(prev, curr)
                assert diff == 0.0, (
                    f"Frame {frame.index}: duplicate should have diff=0.0, got {diff}"
                )
            prev = curr

    def test_diff_ratio_for_unique_frames_above_threshold(
        self,
        analyzer: NumpyAnalyzer,
    ) -> None:
        """Unique frames should have diff_ratio above duplicate_threshold."""
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            duration_sec=1.0,
            pattern=PatternType.COUNTER,
        )
        gen = VideoGenerator(config)

        prev = None
        for frame in gen.iter_frames():
            curr = frame.array.copy()
            if prev is not None and not frame.is_duplicate:
                _, diff = analyzer.compare(prev, curr)
                assert diff >= analyzer.duplicate_threshold, (
                    f"Frame {frame.index}: unique frame should have "
                    f"diff >= {analyzer.duplicate_threshold}, got {diff}"
                )
            prev = curr
