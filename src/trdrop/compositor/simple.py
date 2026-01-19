"""Simple compositor implementation."""

from __future__ import annotations

import numpy as np

from trdrop.compositor.base import Compositor
from trdrop.compositor.types import AggregatedMetrics, CompositorOutput, VideoMetrics
from trdrop.types.frames import FramePair
from trdrop.types.metrics import FrameMetrics
from trdrop.utils.ringbuffer import RingBuffer


class _VideoState:
    """Internal state for a single video stream.

    Uses O(1) memory ring buffer for windowed statistics.
    Stores 1.0 for unique frames, 0.0 for duplicates.
    """

    __slots__ = ("_total_frames", "_total_duplicates", "_window")

    def __init__(self, window_size: int) -> None:
        self._total_frames = 0
        self._total_duplicates = 0
        self._window = RingBuffer(size=window_size, dtype=np.float32)

    def update(self, is_duplicate: bool) -> None:
        self._total_frames += 1
        if is_duplicate:
            self._total_duplicates += 1
        # Store 1.0 for unique, 0.0 for duplicate
        self._window.push(0.0 if is_duplicate else 1.0)

    def windowed_unique_ratio(self) -> float:
        """Ratio of unique frames in the window."""
        return self._window.mean()

    def total_unique_ratio(self) -> float:
        """Ratio of unique frames since start."""
        if self._total_frames == 0:
            return 1.0
        return (self._total_frames - self._total_duplicates) / self._total_frames

    @property
    def total_frames(self) -> int:
        return self._total_frames

    @property
    def total_duplicates(self) -> int:
        return self._total_duplicates

    @property
    def total_unique(self) -> int:
        return self._total_frames - self._total_duplicates

    def reset(self) -> None:
        self._total_frames = 0
        self._total_duplicates = 0
        self._window.clear()


class SimpleCompositor(Compositor):
    """Basic compositor with horizontal layout and text overlays.

    Layout: Videos arranged horizontally, scaled to fit output dimensions.
    Overlays: FPS counter per video (stub - no actual text rendering yet).
    """

    def __init__(
        self,
        video_count: int,
        video_fps: list[float],
        output_width: int = 1920,
        output_height: int = 1080,
        *,
        window_size: int = 60,
    ) -> None:
        if video_count != len(video_fps):
            raise ValueError(
                f"video_count ({video_count}) must match len(video_fps) ({len(video_fps)})"
            )

        self._video_count = video_count
        self._video_fps = video_fps
        self._output_width = output_width
        self._output_height = output_height

        # Pre-allocate output buffer
        self._output_buffer = np.zeros(
            (output_height, output_width, 3), dtype=np.uint8
        )

        # Per-video state
        self._video_states = [
            _VideoState(window_size=window_size) for _ in range(video_count)
        ]

        self._frame_index = 0

    def process(
        self,
        pairs: list[FramePair],
        results: list[FrameMetrics],
    ) -> CompositorOutput:
        if len(pairs) != self._video_count:
            raise ValueError(
                f"Expected {self._video_count} pairs, got {len(pairs)}"
            )
        if len(results) != self._video_count:
            raise ValueError(
                f"Expected {self._video_count} results, got {len(results)}"
            )

        # Update per-video state
        video_metrics: list[VideoMetrics] = []
        for i, (pair, result) in enumerate(zip(pairs, results)):
            state = self._video_states[i]
            is_dup = result.is_duplicate or False
            diff = result.diff_ratio or 0.0

            state.update(is_dup)

            container_fps = self._video_fps[i]
            windowed_fps = container_fps * state.windowed_unique_ratio()
            average_fps = container_fps * state.total_unique_ratio()

            video_metrics.append(
                VideoMetrics(
                    video_index=i,
                    windowed_fps=windowed_fps,
                    average_fps=average_fps,
                    total_frames_processed=state.total_frames,
                    total_duplicates=state.total_duplicates,
                    total_unique=state.total_unique,
                    current_is_duplicate=is_dup,
                    current_diff_ratio=diff,
                )
            )

        # Compose frame (simple horizontal layout)
        self._compose_horizontal(pairs)

        # TODO: Render text overlays (requires font rendering)

        aggregated = AggregatedMetrics(
            frame_index=self._frame_index,
            videos=tuple(video_metrics),
        )

        self._frame_index += 1

        return CompositorOutput(frame=self._output_buffer, metrics=aggregated)

    def _compose_horizontal(self, pairs: list[FramePair]) -> None:
        """Compose frames horizontally into output buffer."""
        if not pairs:
            self._output_buffer.fill(0)
            return

        # Calculate per-video width
        video_width = self._output_width // self._video_count
        remainder = self._output_width % self._video_count

        x_offset = 0
        for i, pair in enumerate(pairs):
            frame = pair.curr.array
            src_h, src_w = frame.shape[:2]

            # Add remainder pixels to last video
            dst_w = video_width + (remainder if i == self._video_count - 1 else 0)
            dst_h = self._output_height

            # Simple nearest-neighbor resize (for stub - replace with proper scaling)
            self._blit_scaled(frame, x_offset, 0, dst_w, dst_h)

            x_offset += dst_w

    def _blit_scaled(
        self,
        src: np.ndarray,
        dst_x: int,
        dst_y: int,
        dst_w: int,
        dst_h: int,
    ) -> None:
        """Blit source to output buffer with scaling."""
        src_h, src_w = src.shape[:2]

        # Calculate scaling factors
        scale_x = src_w / dst_w
        scale_y = src_h / dst_h

        # Generate destination coordinates
        dst_y_end = min(dst_y + dst_h, self._output_height)
        dst_x_end = min(dst_x + dst_w, self._output_width)

        for y in range(dst_y, dst_y_end):
            src_y = int((y - dst_y) * scale_y)
            src_y = min(src_y, src_h - 1)

            for x in range(dst_x, dst_x_end):
                src_x = int((x - dst_x) * scale_x)
                src_x = min(src_x, src_w - 1)

                self._output_buffer[y, x] = src[src_y, src_x]

    def reset(self) -> None:
        for state in self._video_states:
            state.reset()
        self._frame_index = 0
        self._output_buffer.fill(0)

    @property
    def output_shape(self) -> tuple[int, int, int]:
        return (self._output_height, self._output_width, 3)
