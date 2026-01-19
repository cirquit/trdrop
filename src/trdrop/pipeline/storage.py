"""Pre-allocated storage for analysis results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FrameResultSlot:
    """Pre-allocated slot for a single frame's results."""

    pts: int = 0
    has_duplicate: bool = False
    diff_ratio: float = 0.0
    is_duplicate: bool = False
    has_tear: bool = False
    tear_rows: tuple[int, ...] = ()


class VideoResultBuffer:
    """Pre-allocated buffer for all frames of a video."""

    def __init__(self, total_frames: int) -> None:
        self._total_frames = total_frames
        self._slots: list[FrameResultSlot] = [
            FrameResultSlot() for _ in range(total_frames)
        ]
        self._computed_up_to = -1

    @property
    def total_frames(self) -> int:
        return self._total_frames

    @property
    def computed_up_to(self) -> int:
        """Index of the last computed frame, or -1 if none computed."""
        return self._computed_up_to

    def get_slot(self, frame_idx: int) -> FrameResultSlot:
        """Get the result slot for a frame."""
        return self._slots[frame_idx]

    def mark_computed(self, frame_idx: int) -> None:
        """Mark a frame as computed."""
        if frame_idx > self._computed_up_to:
            self._computed_up_to = frame_idx
