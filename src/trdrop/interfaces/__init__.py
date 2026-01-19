"""Abstract interfaces (ABCs)."""

from __future__ import annotations

from trdrop.interfaces.mappable import Mappable
from trdrop.interfaces.source import FrameSource
from trdrop.interfaces.video import VideoReader

__all__ = [
    "FrameSource",
    "Mappable",
    "VideoReader",
]
