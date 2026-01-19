"""Renderer protocol for overlay rendering."""

from __future__ import annotations

from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from trdrop.pipeline.types import VideoFrameState


class Renderer(Protocol):
    """Protocol for frame overlay renderers."""

    def render(
        self,
        frame: NDArray[np.uint8],
        state: VideoFrameState,
    ) -> NDArray[np.uint8]:
        """
        Render overlays onto a frame.

        Args:
            frame: The video frame to render onto (may be modified in-place)
            state: The analysis state for this frame

        Returns:
            The frame with overlays rendered
        """
        ...
