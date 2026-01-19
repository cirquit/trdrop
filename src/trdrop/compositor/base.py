"""Base compositor interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from trdrop.compositor.types import CompositorOutput
from trdrop.types.frames import FramePair
from trdrop.types.metrics import FrameMetrics


class Compositor(ABC):
    """Synchronization point that combines video frames and metrics.

    The compositor:
    1. Takes frame pairs and per-frame analysis results from all videos
    2. Maintains internal state for temporal aggregation (running averages, etc.)
    3. Renders overlays onto a composited output frame
    4. Produces aggregated metrics (windowed FPS, session stats, etc.)

    Lifecycle:
    - Constructed with video metadata (count, resolutions, fps values)
    - process() called once per sync point (frame index)
    - Owns its output buffer (reused each call)
    - reset() to clear state for new session

    Thread safety:
    - process() is NOT thread-safe (single sync point)
    - Export must complete before next process() call (buffer reuse)
    """

    @abstractmethod
    def process(
        self,
        pairs: list[FramePair],
        results: list[FrameMetrics],
    ) -> CompositorOutput:
        """Process a sync point and produce composited output.

        Args:
            pairs: Frame pairs from each video source (same frame index)
            results: Per-frame analysis results for each video

        Returns:
            CompositorOutput with composited frame and aggregated metrics.
            The frame buffer is owned by this compositor and will be
            overwritten on the next call.
        """

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state for a new session.

        Clears running averages, frame counts, etc.
        Does not deallocate buffers.
        """

    @property
    @abstractmethod
    def output_shape(self) -> tuple[int, int, int]:
        """Shape of the output frame (height, width, channels)."""
