"""Streaming CSV exporter."""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import TextIO

from trdrop.compositor.types import CompositorOutput
from trdrop.export.base import StreamingExporter
from trdrop.profiling import get_profiler


class StreamingCSVExporter(StreamingExporter):
    """Writes metrics to CSV incrementally, one row per frame per video.

    Format:
        frame_index,video_index,is_duplicate,diff_ratio,windowed_fps,average_fps
        0,0,False,0.523,60.0,60.0
        0,1,True,0.001,30.0,30.0
        1,0,False,0.412,60.0,60.0
        ...

    Flushes after each frame for crash resilience.
    """

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._file: TextIO | None = None
        self._writer: csv.writer | None = None

    def open(self) -> None:
        self._file = self._path.open("w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow([
            "frame_index",
            "video_index",
            "is_duplicate",
            "diff_ratio",
            "windowed_fps",
            "smoothed_fps",
            "average_fps",
            "frametime_ms",
            "smoothed_frametime_ms",
            "total_frames",
            "total_duplicates",
            "total_unique",
        ])
        self._file.flush()

    def write_frame(self, output: CompositorOutput) -> None:
        if self._writer is None or self._file is None:
            raise RuntimeError("Exporter not opened")

        profiler = get_profiler()
        t0 = time.perf_counter()

        for vm in output.metrics.videos:
            self._writer.writerow([
                output.metrics.frame_index,
                vm.video_index,
                vm.current_is_duplicate,
                f"{vm.current_diff_ratio:.6f}",
                f"{vm.windowed_fps:.2f}",
                f"{vm.smoothed_fps:.2f}",
                f"{vm.average_fps:.2f}",
                f"{vm.current_frametime:.3f}",
                f"{vm.smoothed_frametime:.3f}",
                vm.total_frames_processed,
                vm.total_duplicates,
                vm.total_unique,
            ])
        self._file.flush()

        profiler.add_timing("export_csv", (time.perf_counter() - t0) * 1000)

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
            self._writer = None

    @property
    def path(self) -> Path:
        return self._path
