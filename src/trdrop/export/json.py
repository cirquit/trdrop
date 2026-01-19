"""JSON export for analysis sessions."""

from __future__ import annotations

from pathlib import Path

from trdrop.engine.trdrop import VideoResult


def export_json(
    results: list[VideoResult],
    path: str | Path,
) -> None:
    """
    Export analysis results to JSON.

    TODO: Implement JSON export.

    Args:
        results: List of analysis results
        path: Output file path
    """
    raise NotImplementedError("export_json not yet implemented")


def import_json(path: str | Path) -> list[VideoResult]:
    """
    Import analysis results from JSON.

    TODO: Implement JSON import.

    Args:
        path: Input file path

    Returns:
        List of VideoResult for each video in the session
    """
    raise NotImplementedError("import_json not yet implemented")
