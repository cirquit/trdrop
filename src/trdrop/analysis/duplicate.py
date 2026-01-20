"""Duplicate frame detection."""

from __future__ import annotations

import time

from trdrop.analysis.strategies import (
    CompareStrategy,
    NumbaStride4x4Compare,
    Stride4x4Compare,
    _numba_available,
)
from trdrop.interfaces.mappable import Mappable
from trdrop.profiling import get_profiler
from trdrop.types.frames import FramePair
from trdrop.types.metrics import FrameMetrics


class DuplicateDetector(Mappable[FramePair, FrameMetrics]):
    """Detects duplicate frames by pixel comparison.

    Uses strided sampling (every 4th pixel in both dimensions) for ~97x speedup
    over full pixel comparison. Numba JIT compilation is used when available.

    Fills: is_duplicate, diff_ratio
    """

    def __init__(
        self,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
        strategy: CompareStrategy | None = None,
    ) -> None:
        self._pixel_threshold = pixel_threshold
        self._duplicate_threshold = duplicate_threshold

        # Use provided strategy, or best available default
        if strategy is not None:
            self._strategy = strategy
        elif _numba_available:
            self._strategy = NumbaStride4x4Compare()
        else:
            self._strategy = Stride4x4Compare()

    def map(self, input: FramePair) -> FrameMetrics:
        profiler = get_profiler()
        t0 = time.perf_counter()
        is_dup, diff = self._strategy.compare(
            input.prev.array,
            input.curr.array,
            self._pixel_threshold,
            self._duplicate_threshold,
        )
        profiler.add_timing("analysis_duplicate", (time.perf_counter() - t0) * 1000)
        return FrameMetrics(
            frame_index=input.frame_index,
            is_duplicate=is_dup,
            diff_ratio=diff,
        )
