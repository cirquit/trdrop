"""Preview system for real-time video navigation."""

from __future__ import annotations

from trdrop.pipeline.types import CompositeFrameState


class PreviewSystem:
    """
    Preview system for real-time video navigation.

    TODO: Implement preview functionality:
    - Manage video readers for each loaded video
    - Provide seek_to() for frame navigation
    - Cache recently accessed frames
    - Coordinate with VideoResultBuffer for analysis data
    """

    def seek_to(self, frame_idx: int) -> CompositeFrameState | None:
        """
        Seek to a specific frame and return composite state.

        Args:
            frame_idx: The frame index to seek to

        Returns:
            CompositeFrameState for all videos at this frame, or None if unavailable
        """
        raise NotImplementedError("PreviewSystem.seek_to() not yet implemented")
