"""Types for compositor output."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class VideoMetrics:
    """Aggregated metrics for a single video stream.

    These are temporal aggregations computed by the compositor,
    not per-frame comparison data.
    """

    video_index: int

    # Windowed FPS estimate (e.g., last 60 frames)
    windowed_fps: float

    # Running average FPS since start
    average_fps: float

    # Frame counts
    total_frames_processed: int
    total_duplicates: int
    total_unique: int

    # Current frame info (from latest FrameMetrics)
    current_is_duplicate: bool
    current_diff_ratio: float


@dataclass(frozen=True, slots=True)
class AggregatedMetrics:
    """Combined metrics across all video streams at a sync point.

    Produced by the compositor each frame, contains per-video
    aggregates. GUI/profiling state stored elsewhere.
    """

    frame_index: int

    # Per-video aggregated metrics
    videos: tuple[VideoMetrics, ...]


@dataclass(slots=True)
class CompositorOutput:
    """Output from compositor's process() call.

    Contains the composited frame and aggregated metrics.
    The frame buffer is owned by the compositor and will be
    reused on the next process() call - export must complete
    before next frame.
    """

    # Composited frame with overlays (owned by compositor, reused)
    frame: np.ndarray

    # Aggregated metrics for this sync point
    metrics: AggregatedMetrics

    @property
    def shape(self) -> tuple[int, int, int]:
        return self.frame.shape  # type: ignore[return-value]
