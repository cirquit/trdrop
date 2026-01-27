"""Coordinate translation utilities.

Provides centralized coordinate translation between different reference
frames and coordinate spaces (screen, global, video-local, pixels).
"""

from __future__ import annotations

from dataclasses import dataclass

from trdrop.config.types import (
    FrameLayout,
    GlobalRef,
    Position,
    Reference,
    Size,
    VideoRef,
)


@dataclass
class ViewportState:
    """
    State of the viewport for coordinate translation.

    The viewport shows a potentially zoomed/panned view of the
    full-resolution composited frame.
    """

    # Viewport dimensions in screen pixels
    width: int
    height: int

    # Pan offset (0-1, how much of the frame is scrolled off-screen)
    pan_x: float = 0.0
    pan_y: float = 0.0

    # Zoom factor (1.0 = fit, 2.0 = 200%, etc.)
    zoom: float = 1.0


class CoordinateSystem:
    """
    Centralized coordinate translation with explicit reference frames.

    All translations go through this class to ensure consistency.
    Supports conversion between:
    - Screen coordinates (viewport pixels)
    - Global coordinates (0-1 of entire fused frame)
    - Video-local coordinates (0-1 of a specific video region)
    - Pixel coordinates (output resolution)
    """

    def __init__(self, layout: FrameLayout) -> None:
        """
        Initialize coordinate system.

        Args:
            layout: Frame layout describing video regions and output size
        """
        self._layout = layout

    @property
    def layout(self) -> FrameLayout:
        """Get the current frame layout."""
        return self._layout

    def update_layout(self, layout: FrameLayout) -> None:
        """Update the frame layout."""
        self._layout = layout

    # =========================================================================
    # Position translations
    # =========================================================================

    def position_to_global(self, pos: Position) -> tuple[float, float]:
        """
        Convert Position (with reference) to global coordinates.

        Args:
            pos: Position with explicit reference frame

        Returns:
            (x, y) in global space (0-1)
        """
        return pos.to_global(self._layout)

    def position_to_pixels(self, pos: Position) -> tuple[int, int]:
        """
        Convert Position to pixel coordinates.

        Args:
            pos: Position with explicit reference frame

        Returns:
            (x, y) in pixels at output resolution
        """
        return pos.to_pixels(self._layout)

    def global_to_position(
        self,
        global_x: float,
        global_y: float,
        ref: Reference,
    ) -> Position:
        """
        Convert global coordinates to Position in target reference frame.

        Args:
            global_x: X coordinate in global space (0-1)
            global_y: Y coordinate in global space (0-1)
            ref: Target reference frame

        Returns:
            Position with coordinates relative to the reference frame
        """
        return Position.from_global(global_x, global_y, ref, self._layout)

    # =========================================================================
    # Size translations
    # =========================================================================

    def size_to_global(self, size: Size) -> tuple[float, float]:
        """
        Convert Size (with reference) to global dimensions.

        Args:
            size: Size with explicit reference frame

        Returns:
            (width, height) in global space (0-1)
        """
        return size.to_global(self._layout)

    def size_to_pixels(self, size: Size) -> tuple[int, int]:
        """
        Convert Size to pixel dimensions.

        Args:
            size: Size with explicit reference frame

        Returns:
            (width, height) in pixels at output resolution
        """
        return size.to_pixels(self._layout)

    # =========================================================================
    # Screen translations (for GUI)
    # =========================================================================

    def screen_to_global(
        self,
        screen_x: float,
        screen_y: float,
        viewport: ViewportState,
    ) -> tuple[float, float]:
        """
        Convert screen (viewport) coordinates to global coordinates.

        Accounts for viewport pan and zoom.

        Args:
            screen_x: X in screen/viewport pixels
            screen_y: Y in screen/viewport pixels
            viewport: Current viewport state

        Returns:
            (x, y) in global space (0-1)
        """
        # Normalize to viewport (0-1)
        norm_x = screen_x / viewport.width
        norm_y = screen_y / viewport.height

        # Account for zoom (visible area shrinks as zoom increases)
        visible_width = 1.0 / viewport.zoom
        visible_height = 1.0 / viewport.zoom

        # Apply pan offset and zoom
        global_x = viewport.pan_x + norm_x * visible_width
        global_y = viewport.pan_y + norm_y * visible_height

        return (global_x, global_y)

    def global_to_screen(
        self,
        global_x: float,
        global_y: float,
        viewport: ViewportState,
    ) -> tuple[float, float]:
        """
        Convert global coordinates to screen (viewport) coordinates.

        Args:
            global_x: X in global space (0-1)
            global_y: Y in global space (0-1)
            viewport: Current viewport state

        Returns:
            (x, y) in screen/viewport pixels
        """
        # Remove pan offset
        local_x = global_x - viewport.pan_x
        local_y = global_y - viewport.pan_y

        # Account for zoom
        visible_width = 1.0 / viewport.zoom
        visible_height = 1.0 / viewport.zoom

        # Normalize within visible area
        norm_x = local_x / visible_width
        norm_y = local_y / visible_height

        # Convert to screen pixels
        screen_x = norm_x * viewport.width
        screen_y = norm_y * viewport.height

        return (screen_x, screen_y)

    def screen_to_position(
        self,
        screen_x: float,
        screen_y: float,
        ref: Reference,
        viewport: ViewportState,
    ) -> Position:
        """
        Convert screen coordinates to Position in target reference frame.

        Args:
            screen_x: X in screen/viewport pixels
            screen_y: Y in screen/viewport pixels
            ref: Target reference frame
            viewport: Current viewport state

        Returns:
            Position with coordinates relative to the reference frame
        """
        gx, gy = self.screen_to_global(screen_x, screen_y, viewport)
        return self.global_to_position(gx, gy, ref)

    # =========================================================================
    # Hit testing
    # =========================================================================

    def global_to_video_index(
        self,
        global_x: float,
        global_y: float,
    ) -> int | None:
        """
        Find which video region contains a global point.

        Args:
            global_x: X coordinate in global space (0-1)
            global_y: Y coordinate in global space (0-1)

        Returns:
            Video index or None if outside all regions
        """
        return self._layout.hit_test(global_x, global_y)

    def screen_to_video_index(
        self,
        screen_x: float,
        screen_y: float,
        viewport: ViewportState,
    ) -> int | None:
        """
        Find which video region contains a screen point.

        Args:
            screen_x: X in screen/viewport pixels
            screen_y: Y in screen/viewport pixels
            viewport: Current viewport state

        Returns:
            Video index or None if outside all regions
        """
        gx, gy = self.screen_to_global(screen_x, screen_y, viewport)
        return self.global_to_video_index(gx, gy)

    def is_inside_video(
        self,
        pos: Position,
        video_index: int,
    ) -> bool:
        """
        Check if a position is inside a specific video region.

        Args:
            pos: Position to check
            video_index: Video index to check against

        Returns:
            True if position is inside the video region
        """
        gx, gy = pos.to_global(self._layout)
        region = self._layout.get_region(video_index)
        return region.contains(gx, gy)

    # =========================================================================
    # Reference frame helpers
    # =========================================================================

    def video_ref(self, index: int) -> VideoRef:
        """Create a VideoRef for the given index."""
        return VideoRef(index)

    def global_ref(self) -> GlobalRef:
        """Create a GlobalRef."""
        return GlobalRef()

    def convert_position_ref(
        self,
        pos: Position,
        target_ref: Reference,
    ) -> Position:
        """
        Convert a position to a different reference frame.

        Args:
            pos: Original position
            target_ref: Target reference frame

        Returns:
            New position with same global location but different reference
        """
        return pos.with_ref(target_ref, self._layout)
