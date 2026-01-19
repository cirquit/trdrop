"""CSV export for analysis results."""

from __future__ import annotations

from pathlib import Path

from trdrop.engine.trdrop import VideoResult


def export_csv(
    result: VideoResult,
    path: str | Path,
) -> None:
    """
    Export video analysis results to CSV.

    TODO: Implement CSV export.

    Args:
        result: The analysis result to export
        path: Output file path
    """
    raise NotImplementedError("export_csv not yet implemented")
