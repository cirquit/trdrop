"""Processing buffer for storing frame results during interactive mode.

Enables random access seeking by storing analysis results and compositor
state snapshots for each processed frame.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trdrop.compositor.simple import VideoStateSnapshot
    from trdrop.types.metrics import FrameMetrics


@dataclass(frozen=True, slots=True)
class FrameSnapshot:
    """Complete state snapshot for a single frame.

    Contains everything needed to restore the GUI display at this frame:
    - Analysis metrics (is_duplicate, diff_ratio, etc.)
    - Per-video compositor state (for plot histories)
    """

    frame_idx: int
    metrics: tuple[FrameMetrics, ...]  # One per video
    video_states: tuple[VideoStateSnapshot, ...]  # One per video


class ProcessingBuffer:
    """Buffer for storing processed frame results.

    Stores FrameSnapshot for each processed frame, enabling:
    - Random access to any processed frame by index
    - State restoration for seeking
    - Memory-efficient storage (~1KB per frame per video)

    Memory usage estimate:
        4 videos, 10 minutes @ 60fps = 36K frames
        36K × 4 × ~800 bytes = ~115MB

    Thread safety:
        - append() must be called from processing thread only
        - get() is safe to call from any thread after frame is appended
        - clear() should only be called when processing is stopped
    """

    __slots__ = ("_snapshots", "_video_count")

    def __init__(self, video_count: int) -> None:
        """Initialize buffer.

        Args:
            video_count: Number of videos being processed
        """
        self._video_count = video_count
        self._snapshots: list[FrameSnapshot] = []

    def append(
        self,
        frame_idx: int,
        metrics: tuple[FrameMetrics, ...],
        video_states: tuple[VideoStateSnapshot, ...],
    ) -> None:
        """Append a processed frame's snapshot.

        Args:
            frame_idx: Frame index (must be sequential)
            metrics: Analysis metrics for each video
            video_states: Compositor state snapshot for each video

        Raises:
            ValueError: If frame_idx is not sequential or tuple lengths mismatch
        """
        expected_idx = len(self._snapshots)
        if frame_idx != expected_idx:
            raise ValueError(
                f"Frame index {frame_idx} is not sequential "
                f"(expected {expected_idx})"
            )

        if len(metrics) != self._video_count:
            raise ValueError(
                f"Expected {self._video_count} metrics, got {len(metrics)}"
            )

        if len(video_states) != self._video_count:
            raise ValueError(
                f"Expected {self._video_count} video states, got {len(video_states)}"
            )

        snapshot = FrameSnapshot(
            frame_idx=frame_idx,
            metrics=metrics,
            video_states=video_states,
        )
        self._snapshots.append(snapshot)

    def get(self, frame_idx: int) -> FrameSnapshot:
        """Get snapshot for a frame.

        Args:
            frame_idx: Frame index to retrieve

        Returns:
            FrameSnapshot for the requested frame

        Raises:
            IndexError: If frame_idx is out of range
        """
        if frame_idx < 0 or frame_idx >= len(self._snapshots):
            raise IndexError(
                f"Frame index {frame_idx} out of range "
                f"(0-{len(self._snapshots) - 1})"
            )
        return self._snapshots[frame_idx]

    def clear(self) -> None:
        """Clear all stored snapshots."""
        self._snapshots.clear()

    @property
    def processed_count(self) -> int:
        """Number of frames processed and stored."""
        return len(self._snapshots)

    @property
    def video_count(self) -> int:
        """Number of videos being tracked."""
        return self._video_count

    def __len__(self) -> int:
        """Number of frames stored."""
        return len(self._snapshots)

    def __contains__(self, frame_idx: int) -> bool:
        """Check if frame_idx has been processed."""
        return 0 <= frame_idx < len(self._snapshots)

    def memory_estimate_mb(self) -> float:
        """Estimate memory usage in megabytes.

        Rough estimate: ~800 bytes per video per frame for state snapshots,
        plus ~40 bytes per video per frame for metrics.
        """
        if not self._snapshots:
            return 0.0

        bytes_per_frame = self._video_count * (800 + 40)  # state + metrics
        total_bytes = len(self._snapshots) * bytes_per_frame
        return total_bytes / (1024 * 1024)
