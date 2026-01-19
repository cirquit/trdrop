"""Tests for core analysis engine."""

from __future__ import annotations

import numpy as np
import pytest

from trdrop.analysis.core import (
    AnalysisBuffers,
    NumpyAnalyzer,
    compare_chunk,
    detect_tears_chunk,
)
from trdrop.types.frames import FramePair, FrameView
from trdrop.types.metrics import FrameMetrics


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
        frame_b = np.full((480, 640, 3), 110, dtype=np.uint8)

        is_dup, diff = analyzer.compare(frame_a, frame_b)

        assert is_dup is True

    def test_noise_above_threshold(self) -> None:
        analyzer = NumpyAnalyzer(pixel_threshold=5)
        frame_a = np.full((480, 640, 3), 100, dtype=np.uint8)
        frame_b = np.full((480, 640, 3), 110, dtype=np.uint8)

        is_dup, diff = analyzer.compare(frame_a, frame_b)

        assert is_dup is False

    def test_partial_change_detected(self) -> None:
        analyzer = NumpyAnalyzer()
        frame_a = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b[50:, :] = 255

        is_dup, diff = analyzer.compare(frame_a, frame_b)

        assert is_dup is False
        assert 0.4 < diff < 0.6

    def test_tear_detection_no_tear(self) -> None:
        analyzer = NumpyAnalyzer()
        frame_a = np.zeros((480, 640, 3), dtype=np.uint8)
        frame_b = np.full((480, 640, 3), 255, dtype=np.uint8)

        tears = analyzer.detect_tears(frame_a, frame_b)

        assert len(tears) == 0

    def test_tear_detection_horizontal_split(self) -> None:
        analyzer = NumpyAnalyzer(tear_threshold=0.1)
        frame_a = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b[50:, :] = 255

        tears = analyzer.detect_tears(frame_a, frame_b)

        assert len(tears) >= 1
        assert any(45 <= t <= 55 for t in tears)

    def test_buffer_reuse(self) -> None:
        analyzer = NumpyAnalyzer()
        frame_a = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        frame_b = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

        analyzer.compare(frame_a, frame_b)
        buffers = analyzer.buffers

        analyzer.compare(frame_a, frame_b)
        assert analyzer.buffers is buffers

    def test_buffer_reallocates_on_size_change(self) -> None:
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
    """Tests for chunk-based analysis functions."""

    def test_compare_chunk_identical(self) -> None:
        buf = AnalysisBuffers.allocate(100, 100)
        chunk = np.full((100, 100, 3), 128, dtype=np.uint8)

        diff_pixels, total_pixels = compare_chunk(
            chunk, chunk.copy(), buf.gray_a, buf.gray_b, buf.diff, threshold=10
        )

        assert diff_pixels == 0
        assert total_pixels == 10000

    def test_compare_chunk_different(self) -> None:
        buf = AnalysisBuffers.allocate(100, 100)
        chunk_a = np.zeros((100, 100, 3), dtype=np.uint8)
        chunk_b = np.full((100, 100, 3), 255, dtype=np.uint8)

        diff_pixels, total_pixels = compare_chunk(
            chunk_a, chunk_b, buf.gray_a, buf.gray_b, buf.diff, threshold=10
        )

        assert diff_pixels == total_pixels

    def test_compare_chunk_combines_for_full_frame(self) -> None:
        analyzer = NumpyAnalyzer(pixel_threshold=10, duplicate_threshold=0.01)
        frame_a = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_b[50:, :] = 255

        _, full_diff = analyzer.compare(frame_a, frame_b)

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
        buf = AnalysisBuffers.allocate(50, 100)
        chunk_a = np.zeros((50, 100, 3), dtype=np.uint8)
        chunk_b = np.zeros((50, 100, 3), dtype=np.uint8)
        chunk_b[25:, :] = 255

        tears = detect_tears_chunk(
            chunk_a, chunk_b,
            buf.gray_a, buf.gray_b, buf.diff, buf.row_means,
            threshold=0.1, row_offset=50
        )

        assert len(tears) >= 1
        assert any(70 <= t <= 80 for t in tears)


class TestFrameTypes:
    """Tests for frame data types."""

    def test_frame_pair_release_callback(self) -> None:
        """FramePair.release() should invoke the callback."""
        from trdrop.types.frames import ReleaseCallback

        class TrackingRelease(ReleaseCallback):
            def __init__(self) -> None:
                self.called = False

            def __call__(self) -> None:
                self.called = True

        tracker = TrackingRelease()
        prev_data = np.zeros((10, 10, 3), dtype=np.uint8)
        curr_data = np.zeros((10, 10, 3), dtype=np.uint8)

        pair = FramePair(
            prev=FrameView(_data=prev_data, index=0, pts=0),
            curr=FrameView(_data=curr_data, index=1, pts=1),
            _on_release=tracker,
        )

        assert tracker.called is False
        pair.release()
        assert tracker.called is True

    def test_frame_pair_release_noop_default(self) -> None:
        """FramePair with no callback should have no-op release."""
        prev_data = np.zeros((10, 10, 3), dtype=np.uint8)
        curr_data = np.zeros((10, 10, 3), dtype=np.uint8)

        pair = FramePair(
            prev=FrameView(_data=prev_data, index=0, pts=0),
            curr=FrameView(_data=curr_data, index=1, pts=1),
        )

        # Should not raise
        pair.release()

    def test_frame_view_creation(self) -> None:
        data = np.zeros((480, 640, 3), dtype=np.uint8)
        view = FrameView(_data=data, index=0, pts=1000)

        assert view.index == 0
        assert view.pts == 1000
        assert view.shape == (480, 640, 3)
        assert view.array is data

    def test_frame_view_to_owned(self) -> None:
        data = np.zeros((100, 100, 3), dtype=np.uint8)
        view = FrameView(_data=data, index=0, pts=0)

        owned = view.to_owned()

        assert owned is not data
        assert np.array_equal(owned, data)

    def test_frame_pair_creation(self) -> None:
        prev_data = np.zeros((100, 100, 3), dtype=np.uint8)
        curr_data = np.ones((100, 100, 3), dtype=np.uint8)

        prev = FrameView(_data=prev_data, index=0, pts=0)
        curr = FrameView(_data=curr_data, index=1, pts=1000)

        pair = FramePair(prev=prev, curr=curr)

        assert pair.prev is prev
        assert pair.curr is curr
        assert pair.frame_index == 1


class TestFrameMetrics:
    """Tests for FrameMetrics monoid."""

    def test_empty_creation(self) -> None:
        empty = FrameMetrics.empty(42)

        assert empty.frame_index == 42
        assert empty.is_duplicate is None
        assert empty.diff_ratio is None
        assert empty.tear_rows is None

    def test_partial_creation(self) -> None:
        metrics = FrameMetrics(
            frame_index=10,
            is_duplicate=True,
            diff_ratio=0.005,
        )

        assert metrics.frame_index == 10
        assert metrics.is_duplicate is True
        assert metrics.diff_ratio == 0.005
        assert metrics.tear_rows is None

    def test_monoid_identity(self) -> None:
        empty = FrameMetrics.empty(0)
        partial = FrameMetrics(frame_index=0, is_duplicate=True, diff_ratio=0.01)

        assert empty + partial == partial
        assert partial + empty == partial

    def test_monoid_combine(self) -> None:
        a = FrameMetrics(frame_index=0, is_duplicate=True, diff_ratio=0.01)
        b = FrameMetrics(frame_index=0, tear_rows=(100, 200))

        combined = a + b

        assert combined.frame_index == 0
        assert combined.is_duplicate is True
        assert combined.diff_ratio == 0.01
        assert combined.tear_rows == (100, 200)

    def test_monoid_associativity(self) -> None:
        a = FrameMetrics(frame_index=0, is_duplicate=True, diff_ratio=0.01)
        b = FrameMetrics(frame_index=0, tear_rows=(100,))
        c = FrameMetrics(frame_index=0, frame_time_ms=16.67)

        assert (a + b) + c == a + (b + c)

    def test_monoid_conflict_raises(self) -> None:
        a = FrameMetrics(frame_index=0, is_duplicate=True)
        b = FrameMetrics(frame_index=0, is_duplicate=False)

        with pytest.raises(ValueError, match="Conflicting values"):
            _ = a + b

    def test_monoid_frame_index_mismatch_raises(self) -> None:
        a = FrameMetrics(frame_index=0, is_duplicate=True)
        b = FrameMetrics(frame_index=1, diff_ratio=0.5)

        with pytest.raises(ValueError, match="different frames"):
            _ = a + b
