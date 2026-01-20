"""Tests for interactive mode: snapshots, buffer, and seek functionality.

These tests verify the infrastructure for GUI integration without
requiring actual GUI interaction.
"""

from __future__ import annotations

import numpy as np
import pytest

from trdrop.compositor.simple import _VideoState
from trdrop.engine.buffer import ProcessingBuffer
from trdrop.types.metrics import FrameMetrics
from trdrop.utils.ringbuffer import RingBuffer


class TestRingBufferSnapshot:
    """Tests for RingBuffer snapshot/restore functionality."""

    def test_snapshot_captures_state(self):
        """Snapshot captures all buffer state."""
        buf = RingBuffer(size=10, dtype=np.float32)
        buf.push(1.0)
        buf.push(2.0)
        buf.push(3.0)

        snapshot = buf.snapshot()

        assert snapshot.size == 10
        assert snapshot.count == 3
        assert snapshot.sum == 6.0
        assert snapshot.head == 3

    def test_restore_recovers_exact_state(self):
        """Restore recovers exact buffer state."""
        buf = RingBuffer(size=10, dtype=np.float32)
        buf.push(1.0)
        buf.push(2.0)
        buf.push(3.0)

        snapshot = buf.snapshot()

        # Modify buffer
        buf.push(100.0)
        buf.push(200.0)
        assert list(buf) == [1.0, 2.0, 3.0, 100.0, 200.0]

        # Restore
        buf.restore(snapshot)

        assert list(buf) == [1.0, 2.0, 3.0]
        assert buf.sum() == 6.0
        assert len(buf) == 3

    def test_snapshot_is_immutable(self):
        """Modifying buffer after snapshot doesn't affect snapshot."""
        buf = RingBuffer(size=5, dtype=np.float32)
        buf.push(1.0)
        buf.push(2.0)

        snapshot = buf.snapshot()
        original_sum = snapshot.sum

        # Modify buffer
        buf.push(100.0)

        # Snapshot unchanged
        assert snapshot.sum == original_sum

    def test_restore_full_buffer(self):
        """Restore works correctly for full buffer with wraparound."""
        buf = RingBuffer(size=5, dtype=np.float32)
        for i in range(8):  # Push more than size to trigger wraparound
            buf.push(float(i))

        # Buffer now contains [3, 4, 5, 6, 7]
        assert list(buf) == [3.0, 4.0, 5.0, 6.0, 7.0]

        snapshot = buf.snapshot()

        # Clear and restore
        buf.clear()
        buf.restore(snapshot)

        assert list(buf) == [3.0, 4.0, 5.0, 6.0, 7.0]
        assert buf.sum() == 25.0

    def test_from_snapshot_creates_new_buffer(self):
        """from_snapshot creates a new independent buffer."""
        buf1 = RingBuffer(size=5, dtype=np.float32)
        buf1.push(1.0)
        buf1.push(2.0)

        snapshot = buf1.snapshot()
        buf2 = RingBuffer.from_snapshot(snapshot)

        # Buffers are independent
        buf1.push(100.0)
        assert list(buf1) == [1.0, 2.0, 100.0]
        assert list(buf2) == [1.0, 2.0]

    def test_restore_size_mismatch_raises(self):
        """Restore with mismatched size raises ValueError."""
        buf1 = RingBuffer(size=5, dtype=np.float32)
        buf1.push(1.0)
        snapshot = buf1.snapshot()

        buf2 = RingBuffer(size=10, dtype=np.float32)
        with pytest.raises(ValueError, match="size"):
            buf2.restore(snapshot)


class TestVideoStateSnapshot:
    """Tests for _VideoState snapshot/restore functionality."""

    def test_snapshot_captures_complete_state(self):
        """Snapshot captures all video state."""
        state = _VideoState(window_size=60, container_fps=60.0)

        # Simulate some processing
        state.update(is_duplicate=False)  # unique
        state.update(is_duplicate=True)   # duplicate
        state.update(is_duplicate=False)  # unique

        snapshot = state.snapshot()

        assert snapshot.total_frames == 3
        assert snapshot.total_duplicates == 1
        assert snapshot.container_fps == 60.0

    def test_restore_recovers_state_exactly(self):
        """Restore recovers exact video state."""
        state = _VideoState(window_size=60, container_fps=60.0)

        # Process 10 frames
        for i in range(10):
            state.update(is_duplicate=(i % 3 == 0))

        snapshot = state.snapshot()
        original_fps = state.windowed_fps()
        original_frametime = state.smoothed_frametime()
        original_total = state.total_frames

        # Process more frames
        for i in range(20):
            state.update(is_duplicate=False)

        assert state.total_frames == 30

        # Restore to frame 10
        state.restore(snapshot)

        assert state.total_frames == original_total
        assert state.windowed_fps() == original_fps
        assert state.smoothed_frametime() == original_frametime

    def test_fps_history_preserved(self):
        """FPS history is correctly preserved through snapshot/restore."""
        state = _VideoState(window_size=10, container_fps=60.0)

        # Build up some history
        for i in range(15):
            state.update(is_duplicate=(i % 2 == 0))

        original_history = list(state.fps_history)
        snapshot = state.snapshot()

        # Modify state
        for _ in range(10):
            state.update(is_duplicate=False)

        # History changed
        assert list(state.fps_history) != original_history

        # Restore
        state.restore(snapshot)

        # History restored
        assert list(state.fps_history) == original_history

    def test_frametime_history_preserved(self):
        """Frametime history is correctly preserved."""
        state = _VideoState(window_size=10, container_fps=60.0)

        for i in range(15):
            state.update(is_duplicate=(i % 3 == 0))

        original_frametime_history = list(state.frametime_history)
        snapshot = state.snapshot()

        # Modify
        for _ in range(10):
            state.update(is_duplicate=True)

        # Restore
        state.restore(snapshot)

        assert list(state.frametime_history) == original_frametime_history

    def test_from_snapshot_creates_new_state(self):
        """from_snapshot creates independent state object."""
        state1 = _VideoState(window_size=60, container_fps=60.0)
        for _ in range(5):
            state1.update(is_duplicate=False)

        snapshot = state1.snapshot()
        state2 = _VideoState.from_snapshot(snapshot)

        # States are independent
        state1.update(is_duplicate=True)
        assert state1.total_frames == 6
        assert state2.total_frames == 5


class TestProcessingBuffer:
    """Tests for ProcessingBuffer storage and retrieval."""

    def _make_metrics(self, frame_idx: int, is_dup: bool = False) -> FrameMetrics:
        """Helper to create test metrics."""
        return FrameMetrics(
            frame_index=frame_idx,
            is_duplicate=is_dup,
            diff_ratio=0.1 if is_dup else 0.9,
        )

    def _make_video_state(self, n_frames: int) -> _VideoState:
        """Helper to create video state with n processed frames."""
        state = _VideoState(window_size=60, container_fps=60.0)
        for i in range(n_frames):
            state.update(is_duplicate=(i % 3 == 0))
        return state

    def test_append_and_get(self):
        """Basic append and get functionality."""
        buffer = ProcessingBuffer(video_count=2)

        state1 = self._make_video_state(5)
        state2 = self._make_video_state(5)

        metrics = (self._make_metrics(0), self._make_metrics(0))
        states = (state1.snapshot(), state2.snapshot())

        buffer.append(frame_idx=0, metrics=metrics, video_states=states)

        snapshot = buffer.get(0)
        assert snapshot.frame_idx == 0
        assert len(snapshot.metrics) == 2
        assert len(snapshot.video_states) == 2

    def test_sequential_append_required(self):
        """Append must be sequential."""
        buffer = ProcessingBuffer(video_count=1)

        state = self._make_video_state(1)
        metrics = (self._make_metrics(0),)
        states = (state.snapshot(),)

        buffer.append(0, metrics, states)

        # Skipping frame 1 should fail
        with pytest.raises(ValueError, match="not sequential"):
            buffer.append(2, metrics, states)

    def test_get_out_of_range_raises(self):
        """Get with invalid index raises IndexError."""
        buffer = ProcessingBuffer(video_count=1)

        with pytest.raises(IndexError):
            buffer.get(0)

        state = self._make_video_state(1)
        buffer.append(0, (self._make_metrics(0),), (state.snapshot(),))

        with pytest.raises(IndexError):
            buffer.get(1)

        with pytest.raises(IndexError):
            buffer.get(-1)

    def test_contains(self):
        """__contains__ works correctly."""
        buffer = ProcessingBuffer(video_count=1)

        assert 0 not in buffer

        state = self._make_video_state(1)
        buffer.append(0, (self._make_metrics(0),), (state.snapshot(),))

        assert 0 in buffer
        assert 1 not in buffer

    def test_clear(self):
        """Clear removes all snapshots."""
        buffer = ProcessingBuffer(video_count=1)

        state = self._make_video_state(1)
        for i in range(10):
            buffer.append(i, (self._make_metrics(i),), (state.snapshot(),))

        assert len(buffer) == 10

        buffer.clear()

        assert len(buffer) == 0
        assert 0 not in buffer

    def test_memory_estimate(self):
        """Memory estimate is reasonable."""
        buffer = ProcessingBuffer(video_count=4)

        state = self._make_video_state(1)
        for i in range(1000):
            metrics = tuple(self._make_metrics(i) for _ in range(4))
            states = tuple(state.snapshot() for _ in range(4))
            buffer.append(i, metrics, states)

        # Should be roughly 1000 * 4 * 840 bytes = 3.2MB
        estimate = buffer.memory_estimate_mb()
        assert 2.0 < estimate < 5.0  # Reasonable range


class TestSeekWorkflow:
    """Integration tests for the seek workflow.

    Simulates the interactive mode workflow:
    1. Process frames sequentially, storing snapshots
    2. Seek to an earlier frame
    3. Restore state and verify correctness
    4. Continue processing from seek point
    """

    def test_seek_restores_correct_state(self):
        """Seeking to frame N restores exact state at frame N."""
        # Setup: 2 videos
        buffer = ProcessingBuffer(video_count=2)
        states = [
            _VideoState(window_size=60, container_fps=60.0),
            _VideoState(window_size=60, container_fps=30.0),
        ]

        # Process 100 frames, storing snapshots
        for frame_idx in range(100):
            # Simulate analysis
            is_dup_v0 = (frame_idx % 3 == 0)
            is_dup_v1 = (frame_idx % 5 == 0)

            states[0].update(is_dup_v0)
            states[1].update(is_dup_v1)

            metrics = (
                FrameMetrics(frame_idx, is_duplicate=is_dup_v0, diff_ratio=0.1),
                FrameMetrics(frame_idx, is_duplicate=is_dup_v1, diff_ratio=0.2),
            )
            video_states = (states[0].snapshot(), states[1].snapshot())

            buffer.append(frame_idx, metrics, video_states)

        # Record state at frame 50 for verification
        snapshot_50 = buffer.get(50)
        expected_fps_v0 = list(
            RingBuffer.from_snapshot(snapshot_50.video_states[0].fps_history)
        )
        expected_fps_v1 = list(
            RingBuffer.from_snapshot(snapshot_50.video_states[1].fps_history)
        )

        # Seek to frame 50 by restoring state
        states[0].restore(snapshot_50.video_states[0])
        states[1].restore(snapshot_50.video_states[1])

        # Verify state is correct
        assert states[0].total_frames == 51  # 0-indexed, so frame 50 = 51 frames
        assert list(states[0].fps_history) == expected_fps_v0
        assert list(states[1].fps_history) == expected_fps_v1

    def test_seek_does_not_recompute_analysis(self):
        """Seeking uses cached metrics, doesn't recompute."""
        buffer = ProcessingBuffer(video_count=1)
        state = _VideoState(window_size=60, container_fps=60.0)

        # Track how many times we "compute" metrics
        compute_count = 0

        def compute_metrics(frame_idx: int) -> FrameMetrics:
            nonlocal compute_count
            compute_count += 1
            return FrameMetrics(frame_idx, is_duplicate=False, diff_ratio=0.5)

        # Process 50 frames
        for frame_idx in range(50):
            metrics = compute_metrics(frame_idx)
            state.update(metrics.is_duplicate or False)
            buffer.append(frame_idx, (metrics,), (state.snapshot(),))

        assert compute_count == 50

        # Seek to frame 25 - should NOT recompute
        snapshot = buffer.get(25)
        retrieved_metrics = snapshot.metrics[0]

        # compute_count unchanged - we used cached value
        assert compute_count == 50
        assert retrieved_metrics.frame_index == 25

    def test_continue_processing_after_seek(self):
        """Can continue processing from seek point."""
        buffer = ProcessingBuffer(video_count=1)
        state = _VideoState(window_size=60, container_fps=60.0)

        # Process 100 frames
        for frame_idx in range(100):
            state.update(is_duplicate=(frame_idx % 2 == 0))
            metrics = FrameMetrics(frame_idx, is_duplicate=(frame_idx % 2 == 0))
            buffer.append(frame_idx, (metrics,), (state.snapshot(),))

        # Seek to frame 50
        snapshot_50 = buffer.get(50)
        state.restore(snapshot_50.video_states[0])

        # Clear buffer from frame 51 onwards (simulating re-processing)
        # In real implementation, buffer would support truncation
        # For now, we verify state is correct to continue

        assert state.total_frames == 51

        # Continue processing from frame 51
        state.update(is_duplicate=False)
        assert state.total_frames == 52

    def test_multiple_seeks(self):
        """Can seek multiple times to different frames."""
        buffer = ProcessingBuffer(video_count=1)
        state = _VideoState(window_size=60, container_fps=60.0)

        # Process frames
        for frame_idx in range(100):
            state.update(is_duplicate=(frame_idx % 4 == 0))
            metrics = FrameMetrics(frame_idx, is_duplicate=(frame_idx % 4 == 0))
            buffer.append(frame_idx, (metrics,), (state.snapshot(),))

        # Seek to frame 75
        state.restore(buffer.get(75).video_states[0])
        assert state.total_frames == 76

        # Seek back to frame 25
        state.restore(buffer.get(25).video_states[0])
        assert state.total_frames == 26

        # Seek forward to frame 90
        state.restore(buffer.get(90).video_states[0])
        assert state.total_frames == 91

    def test_seek_preserves_plot_data(self):
        """Plot histories are correctly preserved through seek."""
        buffer = ProcessingBuffer(video_count=1)
        state = _VideoState(window_size=10, container_fps=60.0)

        # Process enough frames to fill the ring buffer
        for frame_idx in range(20):
            # Alternate pattern for interesting plot data
            is_dup = (frame_idx % 3 == 0)
            state.update(is_duplicate=is_dup)
            metrics = FrameMetrics(frame_idx, is_duplicate=is_dup)
            buffer.append(frame_idx, (metrics,), (state.snapshot(),))

        # Get expected plot data at frame 10
        snapshot_10 = buffer.get(10)
        expected_fps_history = list(
            RingBuffer.from_snapshot(snapshot_10.video_states[0].fps_history)
        )
        expected_frametime_history = list(
            RingBuffer.from_snapshot(snapshot_10.video_states[0].frametime_history)
        )

        # Process more frames
        for frame_idx in range(20, 50):
            state.update(is_duplicate=False)

        # Plot data changed
        assert list(state.fps_history) != expected_fps_history

        # Seek to frame 10
        state.restore(snapshot_10.video_states[0])

        # Plot data restored
        assert list(state.fps_history) == expected_fps_history
        assert list(state.frametime_history) == expected_frametime_history
