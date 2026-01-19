"""JSON export for analysis sessions."""

from __future__ import annotations

from pathlib import Path

from trdrop.pipeline.storage import VideoResultBuffer


def export_json(
    buffers: list[VideoResultBuffer],
    path: str | Path,
) -> None:
    """
    Export analysis results to JSON.

    TODO: Adapt to new pipeline types.
    - Accept list of VideoResultBuffer instead of Session
    - Serialize buffer data to JSON format

    Args:
        buffers: List of result buffers for each video
        path: Output file path
    """
    raise NotImplementedError("export_json not yet adapted to new pipeline types")


def import_json(path: str | Path) -> list[VideoResultBuffer]:
    """
    Import analysis results from JSON.

    TODO: Adapt to new pipeline types.

    Args:
        path: Input file path

    Returns:
        List of VideoResultBuffer for each video in the session
    """
    raise NotImplementedError("import_json not yet adapted to new pipeline types")
