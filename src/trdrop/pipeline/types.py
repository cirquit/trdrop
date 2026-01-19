"""Pipeline result types and frame states."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DuplicateResult:
    """Result of duplicate frame detection."""

    diff_ratio: float
    is_duplicate: bool


@dataclass(slots=True)
class TearResult:
    """Result of tear detection."""

    tear_rows: tuple[int, ...]


@dataclass(slots=True)
class VideoFrameState:
    """State of a single video at a specific frame."""

    video_id: int
    frame_idx: int
    pts: int
    duplicate: DuplicateResult | None = None
    tear: TearResult | None = None


@dataclass(slots=True)
class CompositeFrameState:
    """Combined state of all videos at a specific frame index."""

    frame_idx: int
    videos: tuple[VideoFrameState, ...]
