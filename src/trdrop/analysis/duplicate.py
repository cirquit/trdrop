"""Duplicate frame detection."""

from __future__ import annotations

import time

from trdrop.analysis.core import NumpyAnalyzer
from trdrop.interfaces.mappable import Mappable
from trdrop.profiling import get_profiler
from trdrop.types.frames import FramePair
from trdrop.types.metrics import FrameMetrics


class DuplicateDetector(Mappable[FramePair, FrameMetrics]):
    """
    Detects duplicate frames by pixel comparison.

    Fills: is_duplicate, diff_ratio
    """

    def __init__(
        self,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> None:
        self._analyzer = NumpyAnalyzer(
            pixel_threshold=pixel_threshold,
            duplicate_threshold=duplicate_threshold,
        )

    def map(self, input: FramePair) -> FrameMetrics:
        profiler = get_profiler()
        t0 = time.perf_counter()
        is_dup, diff = self._analyzer.compare(
            input.prev.array,
            input.curr.array,
        )
        profiler.add_timing("analysis_duplicate", (time.perf_counter() - t0) * 1000)
        return FrameMetrics(
            frame_index=input.frame_index,
            is_duplicate=is_dup,
            diff_ratio=diff,
        )
