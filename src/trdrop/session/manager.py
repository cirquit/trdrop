"""Session management types."""

from __future__ import annotations

from enum import Enum


class LayoutMode(Enum):
    """Video display layout modes."""

    SINGLE = "single"
    SIDE_BY_SIDE = "side_by_side"
    STACKED = "stacked"
    GRID = "grid"
