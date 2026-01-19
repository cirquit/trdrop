"""Exporter protocol for analysis results."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from trdrop.pipeline.storage import VideoResultBuffer


class Exporter(Protocol):
    """Protocol for exporting analysis results."""

    def export(
        self,
        buffer: VideoResultBuffer,
        path: Path,
    ) -> None:
        """
        Export analysis results to a file.

        Args:
            buffer: The result buffer containing analysis data
            path: The output file path
        """
        ...
