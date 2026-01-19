"""CSV export for analysis results."""

from __future__ import annotations

import csv
from pathlib import Path

from trdrop.engine.trdrop import VideoResult


def export_csv(
    result: VideoResult,
    path: str | Path,
    *,
    include_summary: bool = True,
) -> None:
    """
    Export video analysis results to CSV.

    Format:
        # Summary lines (if include_summary=True)
        frame_index,is_duplicate,diff_ratio,tear_rows
        1,True,0.001,
        2,False,0.523,
        ...

    Args:
        result: The analysis result to export
        path: Output file path
        include_summary: Include summary comment lines at top
    """
    path = Path(path)

    with path.open("w", newline="") as f:
        if include_summary:
            f.write(f"# source: {result.path}\n")
            f.write(f"# fps: {result.fps}\n")
            f.write(f"# total_frames: {result.total_frames}\n")
            f.write(f"# unique_frames: {result.unique_frames}\n")
            f.write(f"# duplicate_frames: {result.duplicate_frames}\n")
            f.write(f"# detected_fps: {result.detected_fps:.2f}\n")
            f.write(f"# duration_sec: {result.duration_sec:.3f}\n")

        writer = csv.writer(f)
        writer.writerow(["frame_index", "is_duplicate", "diff_ratio", "tear_rows"])

        for m in result.metrics:
            tear_str = ";".join(str(r) for r in m.tear_rows) if m.tear_rows else ""
            writer.writerow([
                m.frame_index,
                m.is_duplicate if m.is_duplicate is not None else "",
                f"{m.diff_ratio:.6f}" if m.diff_ratio is not None else "",
                tear_str,
            ])
