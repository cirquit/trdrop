"""Tests for core analysis engine."""

from __future__ import annotations

import numpy as np

from trdrop.core.analyzer import (
    AnalysisBuffers,
    NumpyAnalyzer,
    compare_chunk,
    detect_tears_chunk,
)
from trdrop.pipeline.types import (
    CompositeFrameState,
    DuplicateResult,
    TearResult,
    VideoFrameState,
)


class TestNumpyAnalyzer:
    """Tests for NumpyAnalyzer."""

    def test_identical_frames_are_duplicates(self) -> None:
        analyzer = NumpyAnalyzer()
        frame = np.full((480, 640, 3), 128, dtype=np.uint8)

        is_dup, diff = analyzer.compare(frame, frame.copy())

        assert is_dup is True
        assert diff < 0.01

    def test_different_frames_not_duplicates(self) -> None:
        analyzer = NumpyAnalyzer()
        frame_a = np.zeros((480, 640, 3), dtype=np.uint8)
        frame_b = np.full((480, 640, 3), 255, dtype=np.uint8)

        is_dup, diff = analyzer.compare(frame_a, frame_b)

        assert is_dup is False
        assert diff > 0.9

    def test_small_noise_below_threshold(self) -> None:
        analyzer = NumpyAnalyzer(pixel_threshold=20)
        frame_a = np.full((480, 640, 3), 100, dtype=np.uint8)
        frame_b = np.full((480, 640, 3), 110, dtype=np.uint8)  # +10 diff

        is_dup, diff = analyzer.compare(frame_a, frame_b)

        assert is_dup is True  # Below threshold

    def test_noise_above_threshold(self) -> None:
        analyzer = NumpyAnalyzer(pixel_threshold=5)
        frame_a = np.full((480, 640, 3), 100, dtype=np.uint8)
        frame_b = np.full((480, 640, 3), 110, dtype=np.uint8)  # +10 diff

        is_dup, diff = analyzer.compare(frame_a, frame_b)

        assert is_dup is False  # Above threshold

    def test_partial_change_detected(self) -> None:
        analyzer = NumpyAnalyzer()
        frame_a = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b = np.zeros((100, 100, 3), dtype=np.uint8)

        # Change half the frame
        frame_b[50:, :] = 255

        is_dup, diff = analyzer.compare(frame_a, frame_b)

        assert is_dup is False
        assert 0.4 < diff < 0.6  # Approximately 50%

    def test_tear_detection_no_tear(self) -> None:
        analyzer = NumpyAnalyzer()
        frame_a = np.zeros((480, 640, 3), dtype=np.uint8)
        frame_b = np.full((480, 640, 3), 255, dtype=np.uint8)

        tears = analyzer.detect_tears(frame_a, frame_b)

        # Uniform change = no tear boundary
        assert len(tears) == 0

    def test_tear_detection_horizontal_split(self) -> None:
        analyzer = NumpyAnalyzer(tear_threshold=0.1)

        # Create frames where top half is same, bottom half changed
        frame_a = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b[50:, :] = 255  # Bottom half changed

        tears = analyzer.detect_tears(frame_a, frame_b)

        # Should detect tear at row 50
        assert len(tears) >= 1
        assert any(45 <= t <= 55 for t in tears)  # Near row 50

    def test_buffer_reuse(self) -> None:
        """Test that analyzer reuses internal buffers."""
        analyzer = NumpyAnalyzer()

        frame_a = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        frame_b = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

        # First call allocates buffers
        analyzer.compare(frame_a, frame_b)
        buffers = analyzer.buffers

        # Second call should reuse same buffers
        analyzer.compare(frame_a, frame_b)
        assert analyzer.buffers is buffers

    def test_buffer_reallocates_on_size_change(self) -> None:
        """Test that buffers are reallocated when frame size changes."""
        analyzer = NumpyAnalyzer()

        small_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        large_frame = np.zeros((200, 200, 3), dtype=np.uint8)

        analyzer.compare(small_frame, small_frame)
        small_buffers = analyzer.buffers

        analyzer.compare(large_frame, large_frame)
        large_buffers = analyzer.buffers

        assert small_buffers is not large_buffers
        assert large_buffers is not None
        assert large_buffers.shape == (200, 200)


class TestChunkFunctions:
    """Tests for chunk-based analysis functions (parallelization support)."""

    def test_compare_chunk_identical(self) -> None:
        """Identical chunks should have zero diff pixels."""
        buf = AnalysisBuffers.allocate(100, 100)
        chunk = np.full((100, 100, 3), 128, dtype=np.uint8)

        diff_pixels, total_pixels = compare_chunk(
            chunk, chunk.copy(), buf.gray_a, buf.gray_b, buf.diff, threshold=10
        )

        assert diff_pixels == 0
        assert total_pixels == 10000

    def test_compare_chunk_different(self) -> None:
        """Completely different chunks should have all pixels different."""
        buf = AnalysisBuffers.allocate(100, 100)
        chunk_a = np.zeros((100, 100, 3), dtype=np.uint8)
        chunk_b = np.full((100, 100, 3), 255, dtype=np.uint8)

        diff_pixels, total_pixels = compare_chunk(
            chunk_a, chunk_b, buf.gray_a, buf.gray_b, buf.diff, threshold=10
        )

        assert diff_pixels == total_pixels

    def test_compare_chunk_combines_for_full_frame(self) -> None:
        """Chunk results should combine to match full-frame analysis."""
        analyzer = NumpyAnalyzer(pixel_threshold=10, duplicate_threshold=0.01)

        # Create a frame with top half black, bottom half white
        frame_a = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b[50:, :] = 255

        # Full frame analysis
        _, full_diff = analyzer.compare(frame_a, frame_b)

        # Chunked analysis (two 50-row chunks)
        buf1 = AnalysisBuffers.allocate(50, 100)
        buf2 = AnalysisBuffers.allocate(50, 100)

        diff1, total1 = compare_chunk(
            frame_a[:50], frame_b[:50],
            buf1.gray_a, buf1.gray_b, buf1.diff, threshold=10
        )
        diff2, total2 = compare_chunk(
            frame_a[50:], frame_b[50:],
            buf2.gray_a, buf2.gray_b, buf2.diff, threshold=10
        )

        chunked_diff = (diff1 + diff2) / (total1 + total2)

        assert abs(full_diff - chunked_diff) < 0.001

    def test_detect_tears_chunk_with_offset(self) -> None:
        """Tear detection should apply row offset correctly."""
        buf = AnalysisBuffers.allocate(50, 100)

        chunk_a = np.zeros((50, 100, 3), dtype=np.uint8)
        chunk_b = np.zeros((50, 100, 3), dtype=np.uint8)
        chunk_b[25:, :] = 255  # Bottom half changed

        tears = detect_tears_chunk(
            chunk_a, chunk_b,
            buf.gray_a, buf.gray_b, buf.diff, buf.row_means,
            threshold=0.1, row_offset=50
        )

        # Should detect tear at row 25, but with offset 50 -> row 75
        assert len(tears) >= 1
        assert any(70 <= t <= 80 for t in tears)


class TestPipelineTypes:
    """Tests for new pipeline result types."""

    def test_duplicate_result_creation(self) -> None:
        """Test DuplicateResult dataclass."""
        result = DuplicateResult(diff_ratio=0.05, is_duplicate=True)

        assert result.diff_ratio == 0.05
        assert result.is_duplicate is True

    def test_tear_result_creation(self) -> None:
        """Test TearResult dataclass."""
        result = TearResult(tear_rows=(100, 200, 300))

        assert result.tear_rows == (100, 200, 300)

    def test_tear_result_empty(self) -> None:
        """Test TearResult with no tears."""
        result = TearResult(tear_rows=())

        assert result.tear_rows == ()
        assert len(result.tear_rows) == 0

    def test_video_frame_state_minimal(self) -> None:
        """Test VideoFrameState with minimal fields."""
        state = VideoFrameState(video_id=0, frame_idx=42, pts=1234567)

        assert state.video_id == 0
        assert state.frame_idx == 42
        assert state.pts == 1234567
        assert state.duplicate is None
        assert state.tear is None

    def test_video_frame_state_with_results(self) -> None:
        """Test VideoFrameState with analysis results."""
        dup = DuplicateResult(diff_ratio=0.02, is_duplicate=True)
        tear = TearResult(tear_rows=(150,))

        state = VideoFrameState(
            video_id=1,
            frame_idx=100,
            pts=5000000,
            duplicate=dup,
            tear=tear,
        )

        assert state.video_id == 1
        assert state.frame_idx == 100
        assert state.pts == 5000000
        assert state.duplicate is not None
        assert state.duplicate.is_duplicate is True
        assert state.tear is not None
        assert state.tear.tear_rows == (150,)

    def test_composite_frame_state(self) -> None:
        """Test CompositeFrameState with multiple videos."""
        video_states = (
            VideoFrameState(video_id=0, frame_idx=10, pts=1000),
            VideoFrameState(video_id=1, frame_idx=10, pts=2000),
        )

        composite = CompositeFrameState(frame_idx=10, videos=video_states)

        assert composite.frame_idx == 10
        assert len(composite.videos) == 2
        assert composite.videos[0].video_id == 0
        assert composite.videos[1].video_id == 1
