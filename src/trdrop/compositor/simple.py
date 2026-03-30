"""Simple compositor implementation."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import numpy as np
from PyQt6.QtCore import QPoint, QPointF, QRect, Qt
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPainterPath, QPen

from trdrop.compositor.base import Compositor
from trdrop.compositor.overlay.colors import get_video_color
from trdrop.compositor.overlay.plot import FrameratePlot, FrametimePlot, PlotSeries
from trdrop.compositor.overlay.plot import PlotStyle as OverlayPlotStyle
from trdrop.compositor.overlay.text import FPSText, TextStyle
from trdrop.compositor.scaling import ScaleMode, get_scale_mode_info, has_performance_warning
from trdrop.compositor.types import AggregatedMetrics, CompositorOutput, VideoMetrics
from trdrop.config import (
    FrameLayout,
    PresetConfig,
    compute_layout,
)
from trdrop.profiling import get_profiler
from trdrop.types.frames import FramePair
from trdrop.types.metrics import FrameMetrics
from trdrop.utils.ringbuffer import RingBuffer, RingBufferSnapshot

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class VideoStateSnapshot:
    """Immutable snapshot of video stream state for seek/restore.

    Captures all state needed to restore a _VideoState to a specific
    point in time, enabling frame-accurate seeking in interactive mode.
    """

    total_frames: int
    total_duplicates: int
    unique_window: RingBufferSnapshot
    fps_history: RingBufferSnapshot
    frametime_history: RingBufferSnapshot
    smoothed_fps: float
    smoothed_frametime: float
    last_unique_distance: int
    container_fps: float
    ema_alpha: float


class _VideoState:
    """Internal state for a single video stream.

    Uses O(1) memory ring buffers for windowed statistics.
    Tracks FPS, frametime, and their histories for plotting.
    Provides smoothed values using EMA for stable display.
    """

    __slots__ = (
        "_total_frames",
        "_total_duplicates",
        "_unique_window",
        "_fps_history",
        "_frametime_history",
        "_container_fps",
        "_smoothed_fps",
        "_smoothed_frametime",
        "_ema_alpha",
        "_last_unique_distance",
    )

    def __init__(
        self,
        window_size: int,
        container_fps: float,
        ema_alpha: float = 0.1,
    ) -> None:
        self._total_frames = 0
        self._total_duplicates = 0
        self._container_fps = container_fps
        self._ema_alpha = ema_alpha

        # Window for computing windowed FPS via sum (v1 algorithm)
        # Pre-filled with zeros so FPS = sum(buffer), no extrapolation
        self._unique_window = RingBuffer(size=window_size, dtype=np.float32)
        self._unique_window.prefill(0.0)

        # History of windowed FPS values for plotting
        self._fps_history = RingBuffer(size=window_size, dtype=np.float32)
        self._fps_history.prefill(0.0)

        # History of frametime values for plotting (in ms)
        self._frametime_history = RingBuffer(size=window_size, dtype=np.float32)
        self._frametime_history.prefill(0.0)

        # Smoothed values for display (EMA)
        self._smoothed_fps = 0.0
        self._smoothed_frametime = 0.0

        # Track distance since last unique frame for frametime calculation
        self._last_unique_distance = 0

    def update(self, is_duplicate: bool) -> None:
        self._total_frames += 1
        if is_duplicate:
            self._total_duplicates += 1
            self._last_unique_distance += 1
        else:
            self._last_unique_distance = 0

        # Store 1.0 for unique, 0.0 for duplicate
        self._unique_window.push(0.0 if is_duplicate else 1.0)

        # Windowed FPS = sum of unique frames in window (v1 algorithm)
        windowed_fps = self._unique_window.sum()
        self._fps_history.push(windowed_fps)

        # Calculate instantaneous frametime from last unique frame
        # Frametime = (duplicates + 1) / container_fps * 1000 ms
        current_frametime = self._calculate_current_frametime()
        self._frametime_history.push(current_frametime)

        # Update smoothed values using EMA
        # smoothed = alpha * current + (1 - alpha) * previous
        if self._total_frames == 1:
            self._smoothed_fps = windowed_fps
            self._smoothed_frametime = current_frametime
        else:
            self._smoothed_fps = (
                self._ema_alpha * windowed_fps
                + (1 - self._ema_alpha) * self._smoothed_fps
            )
            if current_frametime > 0:
                self._smoothed_frametime = (
                    self._ema_alpha * current_frametime
                    + (1 - self._ema_alpha) * self._smoothed_frametime
                )

    def _calculate_current_frametime(self) -> float:
        """Calculate frametime based on distance to last unique frame.

        Returns frametime in milliseconds. Returns 0 if no unique frames yet.
        """
        # Look backward in the unique_window to find how many frames
        # since the last unique frame
        window_data = list(self._unique_window)
        if not window_data:
            return 0.0

        # Find the most recent unique frame (value == 1.0)
        frames_since_unique = 0
        found_unique = False

        for i in range(len(window_data) - 1, -1, -1):
            if window_data[i] > 0.5:  # unique frame
                if found_unique:
                    # Found the previous unique, calculate frametime
                    break
                found_unique = True
            if found_unique:
                frames_since_unique += 1

        if not found_unique or frames_since_unique == 0:
            return 0.0

        # Frametime = frames_between_unique / container_fps * 1000
        return (frames_since_unique / self._container_fps) * 1000.0

    def windowed_fps(self) -> float:
        """Windowed FPS = sum of unique frames in window (v1 algorithm)."""
        return self._unique_window.sum()

    def smoothed_fps(self) -> float:
        """EMA-smoothed FPS for stable display."""
        return self._smoothed_fps

    def current_frametime(self) -> float:
        """Current frametime in ms (from history)."""
        data = list(self._frametime_history)
        return data[-1] if data else 0.0

    def smoothed_frametime(self) -> float:
        """EMA-smoothed frametime in ms for stable display."""
        return self._smoothed_frametime

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
    def frametime_history(self) -> RingBuffer:
        """Frametime history for plotting (in ms)."""
        return self._frametime_history

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
        self._frametime_history.prefill(0.0)
        self._smoothed_fps = 0.0
        self._smoothed_frametime = 0.0
        self._last_unique_distance = 0

    def snapshot(self) -> VideoStateSnapshot:
        """Create an immutable snapshot of the current state.

        Used for seeking in interactive mode - capture state at frame N,
        restore later when seeking back to frame N.
        """
        return VideoStateSnapshot(
            total_frames=self._total_frames,
            total_duplicates=self._total_duplicates,
            unique_window=self._unique_window.snapshot(),
            fps_history=self._fps_history.snapshot(),
            frametime_history=self._frametime_history.snapshot(),
            smoothed_fps=self._smoothed_fps,
            smoothed_frametime=self._smoothed_frametime,
            last_unique_distance=self._last_unique_distance,
            container_fps=self._container_fps,
            ema_alpha=self._ema_alpha,
        )

    def restore(self, snapshot: VideoStateSnapshot) -> None:
        """Restore state from a snapshot."""
        self._total_frames = snapshot.total_frames
        self._total_duplicates = snapshot.total_duplicates
        self._unique_window.restore(snapshot.unique_window)
        self._fps_history.restore(snapshot.fps_history)
        self._frametime_history.restore(snapshot.frametime_history)
        self._smoothed_fps = snapshot.smoothed_fps
        self._smoothed_frametime = snapshot.smoothed_frametime
        self._last_unique_distance = snapshot.last_unique_distance

    @classmethod
    def from_snapshot(cls, snapshot: VideoStateSnapshot) -> "_VideoState":
        """Create a new _VideoState from a snapshot."""
        state = cls(
            window_size=snapshot.unique_window.size,
            container_fps=snapshot.container_fps,
            ema_alpha=snapshot.ema_alpha,
        )
        state.restore(snapshot)
        return state


class SimpleCompositor(Compositor):
    """Basic compositor with configurable layout and overlays.

    Layout: Videos arranged according to config (grid, horizontal, vertical).
    Overlays: FPS text and framerate plots (configurable via PresetConfig).

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
        config: PresetConfig | None = None,
        # Legacy parameters for backward compatibility
        fps_texts: list[FPSText] | None = None,
        framerate_plots: list[FrameratePlot] | None = None,
        frametime_plots: list[FrametimePlot] | None = None,
        framerate_combined: bool = True,
        frametime_combined: bool = False,
        video_names: list[str] | None = None,
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

        # Use provided config or create default with HORIZONTAL layout
        # for backward compatibility
        if config is not None:
            self._config = config
        else:
            from trdrop.config import LayoutConfig, LayoutMode
            self._config = PresetConfig()
            self._config.rendering.layout = LayoutConfig(mode=LayoutMode.HORIZONTAL)

        # Compute layout from config
        self._layout = compute_layout(
            video_count,
            self._config.rendering.layout,
            output_width,
            output_height,
        )

        # Ensure video configs exist with correct refs
        self._config.ensure_video_configs(video_count, self._layout)

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
        assert ptr is not None, "QImage.bits() returned None"
        ptr.setsize(output_height * output_width * 3)
        self._output_buffer: np.ndarray = np.frombuffer(
            ptr.asarray(output_height * output_width * 3),  # type: ignore[arg-type]
            dtype=np.uint8,
        ).reshape((output_height, output_width, 3))

        # Per-video state: window_size = ~1 second of frames for each video
        self._video_states = [
            _VideoState(window_size=round(video_fps[i]), container_fps=video_fps[i])
            for i in range(video_count)
        ]

        # Overlay elements - use legacy if provided, otherwise create from config
        self._fps_texts = fps_texts
        self._framerate_plots = framerate_plots
        self._frametime_plots = frametime_plots
        self._framerate_combined = framerate_combined
        self._frametime_combined = frametime_combined

        # If no legacy overlays provided, create from config
        if fps_texts is None and config is not None:
            self._fps_texts = self._create_fps_texts_from_config()
        if framerate_plots is None and config is not None:
            self._framerate_plots = self._create_framerate_plots_from_config()
            self._framerate_combined = True
        if frametime_plots is None and config is not None:
            self._frametime_plots = self._create_frametime_plots_from_config()
            self._frametime_combined = self._video_count == 1

        self._frame_index = 0
        self._video_names = video_names or []

    @staticmethod
    def _make_pixel_font(family: str, pixel_size: int) -> QFont:
        """Create a QFont with pixel size (DPI-independent)."""
        font = QFont(family)
        font.setPixelSize(pixel_size)
        return font

    def _plot_font_px(self, relative_size: float) -> int:
        """Scale plot fonts to the visible video region when using separate overlays."""
        base_height = self._output_height
        if self._video_count > 1:
            _, _, _, base_height = self._video_pixel_bounds(0)
        return max(10, int(relative_size * base_height))

    def _make_plot_style(
        self,
        *,
        line_color: QColor,
        background_color: QColor,
        grid_color: QColor,
        label_size: float,
        line_width: float,
        show_grid: bool,
    ) -> OverlayPlotStyle:
        """Build a plot style tuned for HUD-like overlays."""
        font_px = self._plot_font_px(label_size)
        title_px = max(font_px + 2, int(font_px * 1.18))
        return OverlayPlotStyle(
            line_color=line_color,
            background_color=background_color,
            axis_color=QColor(255, 255, 255, 224),
            grid_color=grid_color,
            text_color=QColor(255, 255, 255, 245),
            shadow_color=QColor(0, 0, 0, 235),
            font=self._make_pixel_font(self._config.rendering.font_family, font_px),
            title_font=self._make_pixel_font(self._config.rendering.font_family, title_px),
            line_width=max(2, int(line_width)),
            show_grid=show_grid,
        )

    def _create_fps_texts_from_config(self) -> list[FPSText]:
        """Create FPS text overlays from config."""
        fps_texts: list[FPSText] = []
        for i in range(self._video_count):
            video_cfg = self._config.get_video_config(i)
            if video_cfg.fps_text.visible and video_cfg.visible:
                # Convert config colors to Qt types
                r, g, b, a = video_cfg.fps_text.color
                color = QColor(r, g, b, a)
                sr, sg, sb, sa = video_cfg.fps_text.shadow_color
                shadow_color = QColor(sr, sg, sb, sa)

                # Calculate font size in pixels from config
                font_size_px = int(
                    video_cfg.fps_text.font_size * self._output_height
                )
                font = QFont(video_cfg.fps_text.font_family)
                font.setPixelSize(font_size_px)
                font.setWeight(QFont.Weight.Bold)

                style = TextStyle(
                    color=color,
                    shadow_color=shadow_color,
                    font=font,
                    shadow_offset=2,
                )
                fps_texts.append(FPSText(style, prefix="FPS:"))
        return fps_texts

    def _create_framerate_plots_from_config(self) -> list[FrameratePlot]:
        """Create framerate plot overlays from config."""
        if not self._config.rendering.fps_plot.visible:
            return []

        cfg = self._config.rendering.fps_plot

        # Convert config colors to Qt types
        r, g, b, a = cfg.background_color
        bg_color = QColor(r, g, b, a)
        gr, gg, gb, ga = cfg.grid_color
        grid_color = QColor(gr, gg, gb, ga)

        plot_count = 1
        plots: list[FrameratePlot] = []
        for i in range(plot_count):
            style = self._make_plot_style(
                line_color=get_video_color(i),
                background_color=bg_color,
                grid_color=grid_color,
                label_size=cfg.label_font_size,
                line_width=cfg.line_width,
                show_grid=cfg.show_grid,
            )
            plots.append(
                FrameratePlot(
                    style,
                    max_fps=max(self._video_fps),
                    title="FRAME-RATE (FPS)",
                    show_center_line=False,
                    auto_scale=True,
                    time_anchor=1.0,
                    show_time_indicator=False,
                    show_start_marker=False,
                )
            )
        return plots

    def _create_frametime_plots_from_config(self) -> list[FrametimePlot]:
        """Create frametime plot overlays from config."""
        if not self._config.rendering.frametime_plot.visible:
            return []

        cfg = self._config.rendering.frametime_plot

        # Convert config colors to Qt types
        r, g, b, a = cfg.background_color
        bg_color = QColor(r, g, b, a)
        gr, gg, gb, ga = cfg.grid_color
        grid_color = QColor(gr, gg, gb, ga)

        plot_count = 1 if self._video_count == 1 else self._video_count
        plots: list[FrametimePlot] = []
        for i in range(plot_count):
            style = self._make_plot_style(
                line_color=get_video_color(i),
                background_color=bg_color,
                grid_color=grid_color,
                label_size=cfg.label_font_size,
                line_width=cfg.line_width,
                show_grid=cfg.show_grid,
            )
            plots.append(
                FrametimePlot(
                    style,
                    max_ms=50.0,
                    title="FRAME-TIME (MS)",
                    auto_scale=True,
                    time_anchor=0.0,
                    show_current_value=False,
                    show_time_indicator=False,
                    show_start_marker=False,
                )
            )
        return plots

    @property
    def layout(self) -> FrameLayout:
        """Current frame layout."""
        return self._layout

    @property
    def config(self) -> PresetConfig:
        """Current config."""
        return self._config

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
                    smoothed_fps=state.smoothed_fps(),
                    average_fps=average_fps,
                    current_frametime=state.current_frametime(),
                    smoothed_frametime=state.smoothed_frametime(),
                    total_frames_processed=state.total_frames,
                    total_duplicates=state.total_duplicates,
                    total_unique=state.total_unique,
                    current_is_duplicate=is_dup,
                    current_diff_ratio=diff,
                )
            )

        # Compose frame using layout from config
        profiler = get_profiler()
        t0 = time.perf_counter()
        self._compose_frames(pairs)
        profiler.add_timing("compositor_compose", (time.perf_counter() - t0) * 1000)

        # Draw overlays if configured
        if self._fps_texts or self._framerate_plots or self._frametime_plots:
            t0 = time.perf_counter()
            self._draw_overlays(video_metrics)
            profiler.add_timing("compositor_overlay", (time.perf_counter() - t0) * 1000)

        aggregated = AggregatedMetrics(
            frame_index=self._frame_index,
            videos=tuple(video_metrics),
        )

        self._frame_index += 1

        return CompositorOutput(frame=self._output_buffer, metrics=aggregated)

    def _compose_frames(self, pairs: list[FramePair]) -> None:
        """Compose frames into output buffer using layout regions."""
        if not pairs:
            self._output_buffer.fill(0)
            return

        # Clear buffer first
        self._output_buffer.fill(0)

        for i, pair in enumerate(pairs):
            frame = pair.curr.array

            # Get region from layout (normalized coords)
            region = self._layout.get_region(i)

            # Convert normalized coords to pixels
            dst_x = int(region.x * self._output_width)
            dst_y = int(region.y * self._output_height)
            dst_w = int(region.width * self._output_width)
            dst_h = int(region.height * self._output_height)

            # Dispatch based on scale mode
            if self._scale_mode == ScaleMode.CROP:
                self._blit_cropped(frame, dst_x, dst_y, dst_w, dst_h)
            elif self._scale_mode == ScaleMode.FIT:
                self._blit_fit(frame, dst_x, dst_y, dst_w, dst_h)
            else:  # STRETCH
                self._blit_stretch(frame, dst_x, dst_y, dst_w, dst_h)

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
        painter = QPainter(self._qimage)

        try:
            # Draw per-video FPS text using config positions
            for i, (state, metrics) in enumerate(zip(self._video_states, video_metrics)):
                if self._fps_texts and i < len(self._fps_texts):
                    video_cfg = self._config.get_video_config(i)
                    if video_cfg.fps_text.visible and video_cfg.visible:
                        t0 = time.perf_counter()
                        # Get position from config (converts to pixels)
                        px, py = video_cfg.fps_text.position.to_pixels(self._layout)
                        self._fps_texts[i].draw(
                            painter,
                            QPoint(px, py),
                            metrics.windowed_fps,
                        )
                        profiler.add_timing(
                            "overlay_fps_text", (time.perf_counter() - t0) * 1000
                        )

            # Draw video file names in top-right of each video region
            if self._video_names:
                self._draw_video_names(painter)

            # Draw framerate plot(s)
            if self._framerate_plots:
                t0 = time.perf_counter()
                if self._framerate_combined:
                    self._draw_framerate_combined(painter)
                else:
                    self._draw_framerate_separate(painter)
                profiler.add_timing(
                    "overlay_framerate_plot", (time.perf_counter() - t0) * 1000
                )

            # Draw frametime plot(s)
            if self._frametime_plots:
                t0 = time.perf_counter()
                if self._frametime_combined:
                    self._draw_frametime_combined(painter, video_metrics)
                else:
                    self._draw_frametime_separate(painter, video_metrics)
                profiler.add_timing(
                    "overlay_frametime_plot", (time.perf_counter() - t0) * 1000
                )

        finally:
            painter.end()

    def _draw_video_names(self, painter: QPainter) -> None:
        """Draw file names in the top-right corner of each video region."""
        painter.save()

        font_size = max(10, int(self._output_height * 0.018))
        font = QFont(self._config.rendering.font_family)
        font.setPixelSize(font_size)
        font.setBold(True)
        painter.setFont(font)

        from PyQt6.QtGui import QFontMetrics
        fm = QFontMetrics(font)
        padding = font_size // 2

        for i, name in enumerate(self._video_names):
            if i >= self._video_count:
                break
            region = self._layout.get_region(i)
            # Region pixel bounds
            rx = int(region.x * self._output_width)
            ry = int(region.y * self._output_height)
            rw = int(region.width * self._output_width)

            text_w = fm.horizontalAdvance(name)
            x = rx + rw - text_w - padding
            y = ry + fm.ascent() + padding

            color = get_video_color(i)

            # Black outline
            path = QPainterPath()
            path.addText(QPointF(x, y), font, name)
            outline_pen = QPen(QColor(0, 0, 0, 200))
            outline_pen.setWidthF(max(2.0, font_size / 8.0))
            outline_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(outline_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

            # Fill with video color
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawPath(path)

        painter.restore()

    def _video_pixel_bounds(self, index: int) -> tuple[int, int, int, int]:
        """Return pixel bounds for a video region."""
        region = self._layout.get_region(index)
        video_px = int(region.x * self._output_width)
        video_py = int(region.y * self._output_height)
        video_pw = int(region.width * self._output_width)
        video_ph = int(region.height * self._output_height)
        return video_px, video_py, video_pw, video_ph

    def _framerate_plot_bounds(self, index: int) -> QRect:
        """Compute per-video framerate plot bounds."""
        video_px, video_py, video_pw, video_ph = self._video_pixel_bounds(index)

        side_margin = max(12, int(video_pw * 0.03))
        bottom_margin = max(14, int(video_ph * 0.035))
        plot_w = max(120, video_pw - (side_margin * 2))
        plot_h = max(72, min(int(video_ph * 0.18), 180))
        plot_x = video_px + side_margin
        plot_y = video_py + video_ph - plot_h - bottom_margin

        return QRect(plot_x, plot_y, plot_w, plot_h)

    def _combined_framerate_plot_bounds(self) -> QRect:
        """Compute global framerate plot bounds from config."""
        cfg = self._config.rendering.fps_plot
        px, py = cfg.position.to_pixels(self._layout)
        pw, ph = cfg.size.to_pixels(self._layout)
        return QRect(px, py, pw, ph)

    def _combined_frametime_strip_bounds(self, index: int) -> QRect:
        """Compute frametime box bounds in a row above the combined framerate plot."""
        fr_bounds = self._combined_framerate_plot_bounds()

        gap = max(12, int(self._output_height * 0.014))
        plot_h = max(64, min(int(self._output_height * 0.095), 108))
        slot_w = max(160, fr_bounds.width() // self._video_count)
        max_fit_w = max(150, slot_w - gap)
        preferred_w = min(320, int(fr_bounds.width() * 0.16))
        plot_w = min(preferred_w, max_fit_w)
        slot_x = fr_bounds.left() + index * slot_w
        plot_x = slot_x + max(0, (slot_w - plot_w) // 2)
        plot_y = max(12, fr_bounds.top() - gap - plot_h)

        return QRect(plot_x, plot_y, plot_w, plot_h)

    def _frametime_plot_bounds(self, index: int) -> QRect:
        """Compute per-video frametime plot bounds as a compact box at lower-left."""
        if self._framerate_combined and self._video_count > 1 and self._framerate_plots:
            return self._combined_frametime_strip_bounds(index)

        video_px, video_py, video_pw, video_ph = self._video_pixel_bounds(index)
        fr_bounds = self._framerate_plot_bounds(index)

        left_margin = max(12, int(video_pw * 0.03))
        gap = max(10, int(video_ph * 0.028))
        top_margin = max(10, int(video_ph * 0.02))
        plot_w = max(160, min(int(video_pw * 0.32), 380))
        plot_h = max(64, min(int(video_ph * 0.11), 120))
        plot_x = video_px + left_margin
        plot_y = fr_bounds.top() - gap - plot_h

        min_y = video_py + top_margin
        if plot_y < min_y:
            plot_y = min_y

        max_w = max(120, video_pw - (left_margin * 2))
        return QRect(plot_x, plot_y, min(plot_w, max_w), plot_h)

    def _draw_framerate_combined(self, painter: QPainter) -> None:
        """Draw a single combined framerate plot with all video series."""
        if not self._framerate_plots:
            return

        plot = self._framerate_plots[0]
        bounds = self._combined_framerate_plot_bounds()

        # Build series list with distinct colors per video
        series_list = [
            PlotSeries(
                history=state.fps_history,
                color=get_video_color(i),
            )
            for i, state in enumerate(self._video_states)
        ]

        plot.draw_combined(painter, bounds, series_list, override_show_title=True)

    def _draw_framerate_separate(self, painter: QPainter) -> None:
        """Draw separate framerate plots for each video."""
        if not self._framerate_plots:
            return

        for i, state in enumerate(self._video_states):
            if i >= len(self._framerate_plots):
                break

            is_last = (i == self._video_count - 1)
            bounds = self._framerate_plot_bounds(i)
            self._framerate_plots[i].draw(
                painter, bounds, state.fps_history,
                override_show_title=is_last,
            )

    def _draw_frametime_combined(
        self,
        painter: QPainter,
        video_metrics: list[VideoMetrics],
    ) -> None:
        """Draw a single combined frametime plot with all video series."""
        if not self._frametime_plots:
            return

        plot = self._frametime_plots[0]
        cfg = self._config.rendering.frametime_plot

        # Get position and size from config (converts to pixels)
        px, py = cfg.position.to_pixels(self._layout)
        pw, ph = cfg.size.to_pixels(self._layout)

        ft_bounds = QRect(px, py, pw, ph)

        series_list = [
            PlotSeries(
                history=state.frametime_history,
                color=get_video_color(i),
            )
            for i, state in enumerate(self._video_states)
        ]

        current_values = [m.smoothed_frametime for m in video_metrics]
        plot.draw_combined(
            painter, ft_bounds, series_list,
            current_values=current_values,
            override_show_title=True,
        )

    def _draw_frametime_separate(
        self,
        painter: QPainter,
        video_metrics: list[VideoMetrics],
    ) -> None:
        """Draw separate frametime plots for each video."""
        if not self._frametime_plots:
            return

        for i, (state, metrics) in enumerate(zip(self._video_states, video_metrics)):
            if i >= len(self._frametime_plots):
                break

            ft_bounds = self._frametime_plot_bounds(i)
            self._frametime_plots[i].draw(
                painter,
                ft_bounds,
                state.frametime_history,
                current_value=metrics.smoothed_frametime,
                override_show_title=True,
            )

    def snapshot_video_states(self) -> tuple[VideoStateSnapshot, ...]:
        """Return immutable snapshots of per-video state.

        Useful for interactive engine seek buffers.
        """
        return tuple(state.snapshot() for state in self._video_states)

    def restore_video_states(self, snapshots: tuple[VideoStateSnapshot, ...]) -> None:
        """Restore per-video state from snapshots (inverse of snapshot)."""
        for i, snap in enumerate(snapshots):
            self._video_states[i].restore(snap)

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
