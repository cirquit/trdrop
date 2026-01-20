"""Simple compositor implementation."""

from __future__ import annotations

import logging
import time

import numpy as np
from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtGui import QImage, QPainter

from trdrop.compositor.base import Compositor
from trdrop.compositor.overlay.plot import FrameratePlot
from trdrop.compositor.overlay.text import FPSText
from trdrop.compositor.scaling import ScaleMode, get_scale_mode_info, has_performance_warning
from trdrop.compositor.types import AggregatedMetrics, CompositorOutput, VideoMetrics
from trdrop.profiling import get_profiler
from trdrop.types.frames import FramePair
from trdrop.types.metrics import FrameMetrics
from trdrop.utils.ringbuffer import RingBuffer

logger = logging.getLogger(__name__)


class _VideoState:
    """Internal state for a single video stream.

    Uses O(1) memory ring buffers for windowed statistics.
    Tracks both unique/duplicate ratio and FPS history for plotting.
    """

    __slots__ = (
        "_total_frames",
        "_total_duplicates",
        "_unique_window",
        "_fps_history",
        "_container_fps",
    )

    def __init__(self, window_size: int, container_fps: float) -> None:
        self._total_frames = 0
        self._total_duplicates = 0
        self._container_fps = container_fps
        # Window for computing windowed FPS via sum (v1 algorithm)
        # Pre-filled with zeros so FPS = sum(buffer), no extrapolation
        self._unique_window = RingBuffer(size=window_size, dtype=np.float32)
        self._unique_window.prefill(0.0)
        # History of windowed FPS values for plotting
        self._fps_history = RingBuffer(size=window_size, dtype=np.float32)
        self._fps_history.prefill(0.0)

    def update(self, is_duplicate: bool) -> None:
        self._total_frames += 1
        if is_duplicate:
            self._total_duplicates += 1

        # Store 1.0 for unique, 0.0 for duplicate
        self._unique_window.push(0.0 if is_duplicate else 1.0)

        # Windowed FPS = sum of unique frames in window (v1 algorithm)
        # Buffer is pre-filled with zeros, so FPS ramps up gradually
        # without oscillation, converging to true FPS after 1 second
        windowed_fps = self._unique_window.sum()
        self._fps_history.push(windowed_fps)

    def windowed_fps(self) -> float:
        """Windowed FPS = sum of unique frames in window (v1 algorithm)."""
        return self._unique_window.sum()

    def total_unique_ratio(self) -> float:
        """Ratio of unique frames since start."""
        if self._total_frames == 0:
            return 1.0
        return (self._total_frames - self._total_duplicates) / self._total_frames

    @property
    def fps_history(self) -> RingBuffer:
        """FPS history for plotting."""
        return self._fps_history

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
        self._unique_window.prefill(0.0)
        self._fps_history.prefill(0.0)


class SimpleCompositor(Compositor):
    """Basic compositor with horizontal layout and overlays.

    Layout: Videos arranged horizontally with configurable scaling mode.
    Overlays: FPS text and framerate plots (optional).

    Scale modes:
        CROP (default): Show center portion, crop excess. Fastest option.
        FIT: Scale to fit with letterboxing. Preserves aspect ratio.
        STRETCH: Scale to fill, ignoring aspect ratio.
    """

    def __init__(
        self,
        video_count: int,
        video_fps: list[float],
        output_width: int = 1920,
        output_height: int = 1080,
        *,
        scale_mode: ScaleMode = ScaleMode.CROP,
        fps_texts: list[FPSText] | None = None,
        framerate_plots: list[FrameratePlot] | None = None,
    ) -> None:
        if video_count != len(video_fps):
            raise ValueError(
                f"video_count ({video_count}) must match len(video_fps) ({len(video_fps)})"
            )

        self._video_count = video_count
        self._video_fps = video_fps
        self._output_width = output_width
        self._output_height = output_height
        self._scale_mode = scale_mode

        # Warn about performance impact of non-CROP modes
        if has_performance_warning(scale_mode):
            info = get_scale_mode_info(scale_mode)
            logger.warning(
                "Compositor using %s mode: %s",
                info.label,
                info.performance_note,
            )

        # Use QImage as backing store, get numpy view into it
        self._qimage = QImage(output_width, output_height, QImage.Format.Format_RGB888)
        self._qimage.fill(0)

        # Create numpy view into QImage's buffer (zero-copy)
        ptr = self._qimage.bits()
        ptr.setsize(output_height * output_width * 3)
        self._output_buffer = np.frombuffer(ptr, dtype=np.uint8).reshape(
            (output_height, output_width, 3)
        )

        # Per-video state: window_size = ~1 second of frames for each video
        self._video_states = [
            _VideoState(window_size=round(video_fps[i]), container_fps=video_fps[i])
            for i in range(video_count)
        ]

        # Overlay elements (optional)
        self._fps_texts = fps_texts
        self._framerate_plots = framerate_plots

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
            windowed_fps = state.windowed_fps()
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
        profiler = get_profiler()
        t0 = time.perf_counter()
        self._compose_horizontal(pairs)
        profiler.add_timing("compositor_compose", (time.perf_counter() - t0) * 1000)

        # Draw overlays if configured
        if self._fps_texts or self._framerate_plots:
            t0 = time.perf_counter()
            self._draw_overlays(video_metrics)
            profiler.add_timing("compositor_overlay", (time.perf_counter() - t0) * 1000)

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

            # Add remainder pixels to last video
            dst_w = video_width + (remainder if i == self._video_count - 1 else 0)
            dst_h = self._output_height

            # Dispatch based on scale mode
            if self._scale_mode == ScaleMode.CROP:
                self._blit_cropped(frame, x_offset, 0, dst_w, dst_h)
            elif self._scale_mode == ScaleMode.FIT:
                self._blit_fit(frame, x_offset, 0, dst_w, dst_h)
            else:  # STRETCH
                self._blit_stretch(frame, x_offset, 0, dst_w, dst_h)

            x_offset += dst_w

    def _blit_cropped(
        self,
        src: np.ndarray,
        dst_x: int,
        dst_y: int,
        dst_w: int,
        dst_h: int,
    ) -> None:
        """Blit source to output buffer, cropping and centering (no scaling).

        Fast path: simple slice assignment, no index computation.
        - If source is larger than slot: center-crop to fit
        - If source is smaller than slot: center with black borders
        """
        src_h, src_w = src.shape[:2]

        # Calculate copy dimensions (minimum of source and destination)
        copy_h = min(src_h, dst_h)
        copy_w = min(src_w, dst_w)

        # Source offsets (center crop if source is larger)
        src_y_start = (src_h - copy_h) // 2
        src_x_start = (src_w - copy_w) // 2

        # Destination offsets (center if source is smaller)
        dst_y_start = dst_y + (dst_h - copy_h) // 2
        dst_x_start = dst_x + (dst_w - copy_w) // 2

        # Clear the slot first if source is smaller (for black borders)
        if copy_h < dst_h or copy_w < dst_w:
            self._output_buffer[dst_y:dst_y + dst_h, dst_x:dst_x + dst_w] = 0

        # Direct slice copy - no scaling, no index arrays
        self._output_buffer[
            dst_y_start:dst_y_start + copy_h,
            dst_x_start:dst_x_start + copy_w,
        ] = src[
            src_y_start:src_y_start + copy_h,
            src_x_start:src_x_start + copy_w,
        ]

    def _blit_fit(
        self,
        src: np.ndarray,
        dst_x: int,
        dst_y: int,
        dst_w: int,
        dst_h: int,
    ) -> None:
        """Blit source to output buffer, scaling to fit with letterboxing.

        Preserves aspect ratio. Adds black bars if aspect ratios differ.
        Uses nearest-neighbor scaling (slow).
        """
        src_h, src_w = src.shape[:2]

        # Calculate scale factor to fit while preserving aspect ratio
        scale_x = dst_w / src_w
        scale_y = dst_h / src_h
        scale = min(scale_x, scale_y)

        # Scaled dimensions
        scaled_w = int(src_w * scale)
        scaled_h = int(src_h * scale)

        # Center in destination slot
        offset_x = dst_x + (dst_w - scaled_w) // 2
        offset_y = dst_y + (dst_h - scaled_h) // 2

        # Clear the slot first (for letterbox bars)
        self._output_buffer[dst_y:dst_y + dst_h, dst_x:dst_x + dst_w] = 0

        # Scale and blit
        self._blit_scaled(src, offset_x, offset_y, scaled_w, scaled_h)

    def _blit_stretch(
        self,
        src: np.ndarray,
        dst_x: int,
        dst_y: int,
        dst_w: int,
        dst_h: int,
    ) -> None:
        """Blit source to output buffer, stretching to fill (ignores aspect ratio).

        Uses nearest-neighbor scaling (slow).
        """
        self._blit_scaled(src, dst_x, dst_y, dst_w, dst_h)

    def _blit_scaled(
        self,
        src: np.ndarray,
        dst_x: int,
        dst_y: int,
        dst_w: int,
        dst_h: int,
    ) -> None:
        """Blit source to output buffer with nearest-neighbor scaling.

        Internal method used by FIT and STRETCH modes. Slow due to
        index array creation and fancy indexing.
        """
        src_h, src_w = src.shape[:2]

        # Clamp destination bounds
        dst_y_end = min(dst_y + dst_h, self._output_height)
        dst_x_end = min(dst_x + dst_w, self._output_width)
        actual_h = dst_y_end - dst_y
        actual_w = dst_x_end - dst_x

        if actual_h <= 0 or actual_w <= 0:
            return

        # Create index arrays for nearest-neighbor sampling (vectorized)
        y_indices = np.minimum(
            (np.arange(actual_h) * src_h // dst_h).astype(np.intp),
            src_h - 1,
        )
        x_indices = np.minimum(
            (np.arange(actual_w) * src_w // dst_w).astype(np.intp),
            src_w - 1,
        )

        # Use fancy indexing to sample and assign in one operation
        self._output_buffer[dst_y:dst_y_end, dst_x:dst_x_end] = src[
            y_indices[:, np.newaxis], x_indices
        ]

    def _draw_overlays(self, video_metrics: list[VideoMetrics]) -> None:
        """Draw FPS text and plots using QPainter directly to QImage buffer."""
        profiler = get_profiler()
        height, width = self._output_height, self._output_width
        painter = QPainter(self._qimage)

        try:
            video_width = width // self._video_count

            for i, (state, metrics) in enumerate(zip(self._video_states, video_metrics)):
                video_x = i * video_width

                # Draw FPS text on every video
                if self._fps_texts and i < len(self._fps_texts):
                    t0 = time.perf_counter()
                    text_x = video_x + int(video_width * 0.05)
                    text_y = int(height * 0.10)
                    self._fps_texts[i].draw(
                        painter,
                        QPoint(text_x, text_y),
                        metrics.windowed_fps,
                    )
                    profiler.add_timing("overlay_fps_text", (time.perf_counter() - t0) * 1000)

                # Draw framerate plot (title only on rightmost video)
                if self._framerate_plots and i < len(self._framerate_plots):
                    plot_height = int(height * 0.20)
                    plot_y = height - plot_height - int(height * 0.05)
                    plot_width = video_width - int(video_width * 0.10)
                    plot_x = video_x + int(video_width * 0.05)

                    bounds = QRect(plot_x, plot_y, plot_width, plot_height)
                    is_last = (i == self._video_count - 1)
                    self._framerate_plots[i].draw(
                        painter, bounds, state.fps_history,
                        override_show_title=is_last,
                    )

        finally:
            painter.end()

    def reset(self) -> None:
        for state in self._video_states:
            state.reset()
        self._frame_index = 0
        self._output_buffer.fill(0)

    @property
    def output_shape(self) -> tuple[int, int, int]:
        return (self._output_height, self._output_width, 3)

    @property
    def scale_mode(self) -> ScaleMode:
        """Current scale mode for video placement."""
        return self._scale_mode
