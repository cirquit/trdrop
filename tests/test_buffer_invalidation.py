"""Tests for buffer invalidation issues in frame sources."""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pytest

from trdrop.interfaces.video import VideoReader
from trdrop.source.mock import MockFrameSource
from trdrop.source.sequential import SequentialFrameSource
from trdrop.types.frames import FramePair


class MockReaderWithKnownFrames(VideoReader):
    """Mock reader that produces known frame content for verification."""

    def __init__(self, num_frames: int = 10) -> None:
        self._num_frames = num_frames
        self._current = 0
        self._width = 100
        self._height = 100

    @property
    def path(self) -> Path:
        return Path("mock://test")

    @property
    def fps(self) -> float:
        return 60.0

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def total_frames(self) -> int:
        return self._num_frames

    def read(self, out: np.ndarray) -> bool:
        if self._current >= self._num_frames:
            return False
        # Fill buffer with frame index value for easy verification
        out.fill(self._current)
        self._current += 1
        return True

    def seek(self, frame_index: int) -> None:
        self._current = frame_index

    def close(self) -> None:
        pass


class TestBufferInvalidation:
    """Tests demonstrating buffer invalidation behavior."""

    def test_sequential_source_invalidates_previous_frame(self) -> None:
        """
        Demonstrates that SequentialFrameSource invalidates previous frames
        when release() is not called (legacy behavior with warning).
        """
        reader = MockReaderWithKnownFrames(num_frames=5)
        source = SequentialFrameSource(reader)

        stored_pairs: list[FramePair] = []

        # Expect warnings about missing release() calls
        with pytest.warns(RuntimeWarning, match="FramePair not released"):
            for pair in source:
                stored_pairs.append(pair)
                # Deliberately NOT calling pair.release() to test old behavior

        # Due to buffer reuse, stored_pairs[0].prev should have been overwritten
        pair0_prev_expected = 0
        pair0_curr_expected = 1

        pair0_prev_actual = stored_pairs[0].prev.array[0, 0, 0]
        pair0_curr_actual = stored_pairs[0].curr.array[0, 0, 0]

        # The buffers WILL be invalid - this is the documented behavior
        buffers_invalidated = (
            pair0_prev_actual != pair0_prev_expected
            or pair0_curr_actual != pair0_curr_expected
        )
        assert buffers_invalidated, (
            "If this passes, buffers were NOT invalidated - check implementation"
        )

    def test_sequential_source_current_pair_valid_during_iteration(self) -> None:
        """
        Verifies that the CURRENT frame pair is valid during iteration
        when using proper release() pattern.
        """
        reader = MockReaderWithKnownFrames(num_frames=5)
        source = SequentialFrameSource(reader)

        # No warnings expected when release() is called properly
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # Treat warnings as errors
            for pair in source:
                # During iteration, current pair should be valid
                prev_idx = pair.prev.index
                curr_idx = pair.curr.index

                prev_value = pair.prev.array[0, 0, 0]
                curr_value = pair.curr.array[0, 0, 0]

                # Values should match frame indices
                assert prev_value == prev_idx, f"prev frame {prev_idx} has value {prev_value}"
                assert curr_value == curr_idx, f"curr frame {curr_idx} has value {curr_value}"

                # Proper usage: release when done
                pair.release()

    def test_holding_reference_causes_data_corruption(self) -> None:
        """
        Demonstrates that holding a reference to a previous FramePair
        without releasing leads to data corruption when the source advances.
        """
        reader = MockReaderWithKnownFrames(num_frames=5)
        source = SequentialFrameSource(reader)
        source_iter = iter(source)

        # Get first pair
        pair1 = next(source_iter)
        assert pair1.prev.array[0, 0, 0] == 0  # Frame 0
        assert pair1.curr.array[0, 0, 0] == 1  # Frame 1

        # Store references to the arrays
        pair1_prev_ref = pair1.prev.array
        pair1_curr_ref = pair1.curr.array

        # Advance to next pair WITHOUT releasing - expect warning
        with pytest.warns(RuntimeWarning, match="FramePair not released"):
            pair2 = next(source_iter)

        # pair2 is valid
        assert pair2.prev.array[0, 0, 0] == 1  # Frame 1
        assert pair2.curr.array[0, 0, 0] == 2  # Frame 2

        # But pair1's buffers are now corrupted!
        # One of them was reused for the new read
        pair1_prev_now = pair1_prev_ref[0, 0, 0]
        pair1_curr_now = pair1_curr_ref[0, 0, 0]

        # At least one buffer should be different (overwritten)
        buffers_changed = (pair1_prev_now != 0) or (pair1_curr_now != 1)

        assert buffers_changed, (
            f"Expected buffer invalidation. "
            f"pair1_prev was 0, now {pair1_prev_now}. "
            f"pair1_curr was 1, now {pair1_curr_now}."
        )

    def test_mock_source_allocates_per_iteration(self) -> None:
        """
        MockFrameSource allocates new buffers each iteration,
        so previous pairs remain valid (but uses more memory).
        """
        source = MockFrameSource(total_frames=5)

        stored_pairs: list[FramePair] = []
        for pair in source:
            stored_pairs.append(pair)

        # All stored pairs should still be valid
        for i, pair in enumerate(stored_pairs):
            expected_curr = (i + 1) % 256
            actual_curr = pair.curr.array[0, 0, 0]
            assert actual_curr == expected_curr, (
                f"Pair {i}: expected curr value {expected_curr}, got {actual_curr}"
            )
