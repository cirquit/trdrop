"""CSV export for analysis results."""

from __future__ import annotations

from pathlib import Path

from trdrop.pipeline.storage import VideoResultBuffer


def export_csv(
    buffer: VideoResultBuffer,
    path: str | Path,
    container_fps: float = 60.0,
) -> None:
    """
    Export video analysis results to CSV.

    TODO: Adapt to new pipeline types.
    - Read from VideoResultBuffer instead of VideoAnalysis
    - Calculate real_fps from buffer data
    - Calculate frametime from buffer data

    Args:
        buffer: The result buffer containing analysis data
        path: Output file path
        container_fps: Container framerate for calculations
    """
    raise NotImplementedError("export_csv not yet adapted to new pipeline types")
