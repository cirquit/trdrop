"""Configuration types with explicit reference frames.

All positions use normalized coordinates (0-1) with an explicit reference
frame indicating what the coordinates are relative to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# =============================================================================
# Layout Types (needed by Position/Size)
# =============================================================================


@dataclass(frozen=True, slots=True)
class VideoRegion:
    """
    Region of a video within the fused frame.

    All coordinates are normalized (0-1).
    """

    index: int
    x: float
    y: float
    width: float
    height: float

    @property
    def rect(self) -> tuple[float, float, float, float]:
        """Return (x, y, width, height) tuple."""
        return (self.x, self.y, self.width, self.height)

    def contains(self, global_x: float, global_y: float) -> bool:
        """Check if a global point is within this region."""
        return (
            self.x <= global_x < self.x + self.width
            and self.y <= global_y < self.y + self.height
        )


@dataclass(frozen=True, slots=True)
class FrameLayout:
    """
    Layout information for the fused frame.

    Describes how videos are arranged and the output resolution.
    """

    regions: tuple[VideoRegion, ...]
    output_width: int
    output_height: int

    @property
    def video_count(self) -> int:
        """Number of videos in this layout."""
        return len(self.regions)

    def get_region(self, index: int) -> VideoRegion:
        """Get region for video at index."""
        for region in self.regions:
            if region.index == index:
                return region
        raise IndexError(f"No region for video index {index}")

    def hit_test(self, global_x: float, global_y: float) -> int | None:
        """
        Find which video region contains a global point.

        Args:
            global_x: X coordinate (0-1)
            global_y: Y coordinate (0-1)

        Returns:
            Video index or None if outside all regions
        """
        for region in self.regions:
            if region.contains(global_x, global_y):
                return region.index
        return None


# =============================================================================
# Reference Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class GlobalRef:
    """Reference to the entire fused frame."""

    def __repr__(self) -> str:
        return "GlobalRef()"


@dataclass(frozen=True, slots=True)
class VideoRef:
    """Reference to a specific video's region within the fused frame."""

    index: int

    def __repr__(self) -> str:
        return f"VideoRef({self.index})"


Reference = GlobalRef | VideoRef


# =============================================================================
# Position and Size
# =============================================================================


@dataclass(frozen=True, slots=True)
class Position:
    """
    A position with explicit frame of reference.

    Coordinates are normalized (0-1) within the reference frame.
    """

    x: float
    y: float
    ref: Reference

    def to_global(self, layout: FrameLayout) -> tuple[float, float]:
        """Convert to global coordinates (0-1 of entire fused frame)."""
        match self.ref:
            case GlobalRef():
                return (self.x, self.y)
            case VideoRef(index=idx):
                region = layout.regions[idx]
                return (
                    region.x + self.x * region.width,
                    region.y + self.y * region.height,
                )

    def to_pixels(self, layout: FrameLayout) -> tuple[int, int]:
        """Convert to pixel coordinates in output resolution."""
        gx, gy = self.to_global(layout)
        return (
            int(gx * layout.output_width),
            int(gy * layout.output_height),
        )

    @classmethod
    def from_global(
        cls,
        global_x: float,
        global_y: float,
        ref: Reference,
        layout: FrameLayout,
    ) -> Position:
        """
        Create position from global coords, storing in target reference frame.

        Args:
            global_x: X coordinate in global space (0-1)
            global_y: Y coordinate in global space (0-1)
            ref: Target reference frame to store position in
            layout: Frame layout for coordinate translation

        Returns:
            Position with coordinates relative to the target reference frame
        """
        match ref:
            case GlobalRef():
                return cls(global_x, global_y, ref)
            case VideoRef(index=idx):
                region = layout.regions[idx]
                local_x = (global_x - region.x) / region.width
                local_y = (global_y - region.y) / region.height
                return cls(local_x, local_y, ref)

    def with_ref(self, ref: Reference, layout: FrameLayout) -> Position:
        """Convert this position to a different reference frame."""
        gx, gy = self.to_global(layout)
        return Position.from_global(gx, gy, ref, layout)


@dataclass(frozen=True, slots=True)
class Size:
    """
    A size with explicit frame of reference.

    Dimensions are normalized (0-1) within the reference frame.
    """

    width: float
    height: float
    ref: Reference

    def to_global(self, layout: FrameLayout) -> tuple[float, float]:
        """Convert to global size (0-1 of entire fused frame)."""
        match self.ref:
            case GlobalRef():
                return (self.width, self.height)
            case VideoRef(index=idx):
                region = layout.regions[idx]
                return (
                    self.width * region.width,
                    self.height * region.height,
                )

    def to_pixels(self, layout: FrameLayout) -> tuple[int, int]:
        """Convert to pixel dimensions in output resolution."""
        gw, gh = self.to_global(layout)
        return (
            int(gw * layout.output_width),
            int(gh * layout.output_height),
        )


# =============================================================================
# Anchor Points
# =============================================================================


class Anchor(Enum):
    """Anchor point for positioning elements."""

    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


# =============================================================================
# Overlay Configs
# =============================================================================


@dataclass
class FpsTextConfig:
    """Configuration for FPS text overlay."""

    position: Position = field(
        default_factory=lambda: Position(0.05, 0.05, GlobalRef())
    )
    anchor: Anchor = Anchor.TOP_LEFT
    visible: bool = True
    font_size: float = 0.03  # Relative to reference frame height
    font_family: str = "monospace"
    color: tuple[int, int, int, int] = (255, 255, 255, 230)  # RGBA
    shadow: bool = True
    shadow_color: tuple[int, int, int, int] = (0, 0, 0, 180)


@dataclass
class FrametimeTextConfig:
    """Configuration for frametime text overlay."""

    position: Position = field(
        default_factory=lambda: Position(0.05, 0.10, GlobalRef())
    )
    anchor: Anchor = Anchor.TOP_LEFT
    visible: bool = True
    font_size: float = 0.025
    font_family: str = "monospace"
    color: tuple[int, int, int, int] = (255, 255, 255, 230)
    shadow: bool = True
    shadow_color: tuple[int, int, int, int] = (0, 0, 0, 180)


class PlotStyle(Enum):
    """Style for rendering plots."""

    LINE = "line"
    FILLED = "filled"
    BAR = "bar"


@dataclass
class FpsPlotConfig:
    """Configuration for FPS plot overlay (global, spans all videos)."""

    position: Position = field(
        default_factory=lambda: Position(0.05, 0.85, GlobalRef())
    )
    size: Size = field(
        default_factory=lambda: Size(0.9, 0.12, GlobalRef())
    )
    visible: bool = True
    style: PlotStyle = PlotStyle.FILLED
    background_color: tuple[int, int, int, int] = (0, 0, 0, 128)
    grid_color: tuple[int, int, int, int] = (128, 128, 128, 64)
    line_width: float = 2.0
    show_grid: bool = True


@dataclass
class FrametimePlotConfig:
    """Configuration for frametime plot overlay (global)."""

    position: Position = field(
        default_factory=lambda: Position(0.05, 0.70, GlobalRef())
    )
    size: Size = field(
        default_factory=lambda: Size(0.9, 0.12, GlobalRef())
    )
    visible: bool = False  # Off by default
    style: PlotStyle = PlotStyle.LINE
    background_color: tuple[int, int, int, int] = (0, 0, 0, 128)
    grid_color: tuple[int, int, int, int] = (128, 128, 128, 64)
    line_width: float = 2.0
    show_grid: bool = True


# =============================================================================
# Per-Video Config
# =============================================================================


@dataclass
class VideoOverlayConfig:
    """
    Per-video overlay configuration.

    Note: Default positions use GlobalRef() as placeholder.
    When assigned to a video index, positions should be updated
    to use VideoRef(index) via update_refs().
    """

    fps_text: FpsTextConfig = field(default_factory=FpsTextConfig)
    frametime_text: FrametimeTextConfig = field(default_factory=FrametimeTextConfig)
    # Per-video visibility (can hide individual video overlays)
    visible: bool = True

    def update_refs(self, video_index: int, layout: FrameLayout) -> VideoOverlayConfig:
        """
        Return a copy with all positions converted to reference this video.

        Args:
            video_index: The video index to reference
            layout: Frame layout for coordinate translation

        Returns:
            New VideoOverlayConfig with updated references
        """
        ref = VideoRef(video_index)
        return VideoOverlayConfig(
            fps_text=FpsTextConfig(
                position=self.fps_text.position.with_ref(ref, layout),
                anchor=self.fps_text.anchor,
                visible=self.fps_text.visible,
                font_size=self.fps_text.font_size,
                font_family=self.fps_text.font_family,
                color=self.fps_text.color,
                shadow=self.fps_text.shadow,
                shadow_color=self.fps_text.shadow_color,
            ),
            frametime_text=FrametimeTextConfig(
                position=self.frametime_text.position.with_ref(ref, layout),
                anchor=self.frametime_text.anchor,
                visible=self.frametime_text.visible,
                font_size=self.frametime_text.font_size,
                font_family=self.frametime_text.font_family,
                color=self.frametime_text.color,
                shadow=self.frametime_text.shadow,
                shadow_color=self.frametime_text.shadow_color,
            ),
            visible=self.visible,
        )


# =============================================================================
# Processing and Export Configs
# =============================================================================


@dataclass
class ProcessingConfig:
    """Configuration for video analysis processing."""

    duplicate_threshold: float = 0.02
    window_size: int = 60


class LayoutMode(Enum):
    """How videos are arranged in the fused output."""

    SINGLE = "single"  # One video at a time
    HORIZONTAL = "horizontal"  # Side by side
    VERTICAL = "vertical"  # Stacked
    GRID = "grid"  # 2x2 grid


@dataclass
class LayoutConfig:
    """Configuration for video layout in fused output."""

    mode: LayoutMode = LayoutMode.GRID
    spacing: float = 0.0  # Normalized gap between videos


@dataclass
class RenderingConfig:
    """Global rendering configuration (shared across all videos)."""

    layout: LayoutConfig = field(default_factory=LayoutConfig)
    fps_plot: FpsPlotConfig = field(default_factory=FpsPlotConfig)
    frametime_plot: FrametimePlotConfig = field(default_factory=FrametimePlotConfig)
    font_family: str = "monospace"
    # Colors for each video's data in plots
    video_colors: tuple[tuple[int, int, int, int], ...] = (
        (52, 199, 89, 230),   # Green
        (0, 122, 255, 230),   # Blue
        (255, 149, 0, 230),   # Orange
        (255, 59, 48, 230),   # Red
    )


class VideoCodec(Enum):
    """Supported video codecs for export."""

    H264 = "h264"
    H265 = "h265"
    VP9 = "vp9"
    PRORES = "prores"


@dataclass
class ExportConfig:
    """Configuration for video export."""

    resolution: tuple[int, int] = (1920, 1080)
    codec: VideoCodec = VideoCodec.H264
    bitrate: str = "auto"  # "auto" or specific like "10M"
    fps: float | None = None  # None = use source fps


# =============================================================================
# Main Preset Config
# =============================================================================


@dataclass
class PresetConfig:
    """
    Complete preset configuration.

    Contains all settings for processing, rendering, and export.
    Videos dict uses sparse indexing - keys are video indices,
    missing indices use defaults.
    """

    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    rendering: RenderingConfig = field(default_factory=RenderingConfig)
    videos: dict[int, VideoOverlayConfig] = field(default_factory=dict)
    export: ExportConfig = field(default_factory=ExportConfig)

    def get_video_config(self, index: int) -> VideoOverlayConfig:
        """
        Get config for video at index.

        Returns existing config or creates default.
        Note: Default config has GlobalRef positions - caller should
        call update_refs() with layout if VideoRef is needed.
        """
        if index not in self.videos:
            self.videos[index] = VideoOverlayConfig()
        return self.videos[index]

    def ensure_video_configs(
        self, video_count: int, layout: FrameLayout
    ) -> None:
        """
        Ensure configs exist for all video indices with correct refs.

        Args:
            video_count: Number of videos to ensure configs for
            layout: Frame layout for coordinate translation
        """
        for i in range(video_count):
            if i not in self.videos:
                default = VideoOverlayConfig()
                self.videos[i] = default.update_refs(i, layout)
