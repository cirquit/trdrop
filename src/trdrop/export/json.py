"""JSON export for analysis sessions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trdrop.engine.trdrop import VideoResult
from trdrop.types.metrics import FrameMetrics

_FORMAT_VERSION = 1


def _metrics_to_dict(m: FrameMetrics) -> dict[str, Any]:
    """Convert FrameMetrics to JSON-serializable dict."""
    d: dict[str, Any] = {"frame_index": m.frame_index}
    if m.is_duplicate is not None:
        d["is_duplicate"] = m.is_duplicate
    if m.diff_ratio is not None:
        d["diff_ratio"] = m.diff_ratio
    if m.tear_rows is not None:
        d["tear_rows"] = list(m.tear_rows)
    if m.frame_time_ms is not None:
        d["frame_time_ms"] = m.frame_time_ms
    return d


def _dict_to_metrics(d: dict[str, Any]) -> FrameMetrics:
    """Convert dict back to FrameMetrics."""
    tear_rows = d.get("tear_rows")
    return FrameMetrics(
        frame_index=d["frame_index"],
        is_duplicate=d.get("is_duplicate"),
        diff_ratio=d.get("diff_ratio"),
        tear_rows=tuple(tear_rows) if tear_rows is not None else None,
        frame_time_ms=d.get("frame_time_ms"),
    )


def _result_to_dict(result: VideoResult) -> dict[str, Any]:
    """Convert VideoResult to JSON-serializable dict."""
    return {
        "path": str(result.path),
        "fps": result.fps,
        "total_frames": result.total_frames,
        "summary": {
            "unique_frames": result.unique_frames,
            "duplicate_frames": result.duplicate_frames,
            "detected_fps": result.detected_fps,
            "duration_sec": result.duration_sec,
        },
        "metrics": [_metrics_to_dict(m) for m in result.metrics],
    }


def _dict_to_result(d: dict[str, Any]) -> VideoResult:
    """Convert dict back to VideoResult."""
    return VideoResult(
        path=Path(d["path"]),
        fps=d["fps"],
        total_frames=d["total_frames"],
        metrics=tuple(_dict_to_metrics(m) for m in d["metrics"]),
    )


def export_json(
    results: list[VideoResult],
    path: str | Path,
    *,
    indent: int | None = 2,
) -> None:
    """
    Export analysis results to JSON.

    Format:
        {
            "version": 1,
            "videos": [
                {
                    "path": "video.mp4",
                    "fps": 60.0,
                    "total_frames": 120,
                    "summary": {...},
                    "metrics": [...]
                }
            ]
        }

    Args:
        results: List of analysis results
        path: Output file path
        indent: JSON indentation (None for compact)
    """
    path = Path(path)

    data = {
        "version": _FORMAT_VERSION,
        "videos": [_result_to_dict(r) for r in results],
    }

    with path.open("w") as f:
        json.dump(data, f, indent=indent)


def import_json(path: str | Path) -> list[VideoResult]:
    """
    Import analysis results from JSON.

    Args:
        path: Input file path

    Returns:
        List of VideoResult for each video in the session

    Raises:
        ValueError: If format version is unsupported
    """
    path = Path(path)

    with path.open() as f:
        data = json.load(f)

    version = data.get("version", 0)
    if version != _FORMAT_VERSION:
        raise ValueError(
            f"Unsupported JSON format version {version}, expected {_FORMAT_VERSION}"
        )

    return [_dict_to_result(v) for v in data["videos"]]
