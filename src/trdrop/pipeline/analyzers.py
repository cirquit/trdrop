"""Frame analyzers wrapping core NumpyAnalyzer with owned buffers."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from trdrop.core.analyzer import AnalysisBuffers, NumpyAnalyzer
from trdrop.pipeline.types import DuplicateResult, TearResult


class DuplicateAnalyzer:
    """Wraps NumpyAnalyzer.compare() with owned buffers."""

    def __init__(
        self,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> None:
        self._core = NumpyAnalyzer(
            pixel_threshold=pixel_threshold,
            duplicate_threshold=duplicate_threshold,
        )

    def analyze(
        self,
        prev: NDArray[np.uint8],
        curr: NDArray[np.uint8],
    ) -> DuplicateResult:
        """Compare two frames and return duplicate detection result."""
        is_duplicate, diff_ratio = self._core.compare(prev, curr)
        return DuplicateResult(diff_ratio=diff_ratio, is_duplicate=is_duplicate)

    @property
    def buffers(self) -> AnalysisBuffers | None:
        """Get the internal analysis buffers."""
        return self._core.buffers


class TearAnalyzer:
    """Wraps NumpyAnalyzer.detect_tears() with owned buffers."""

    def __init__(self, tear_threshold: float = 0.3) -> None:
        self._core = NumpyAnalyzer(tear_threshold=tear_threshold)

    def analyze(
        self,
        prev: NDArray[np.uint8],
        curr: NDArray[np.uint8],
    ) -> TearResult:
        """Detect tears between two frames."""
        tear_rows = self._core.detect_tears(prev, curr)
        return TearResult(tear_rows=tuple(tear_rows))

    @property
    def buffers(self) -> AnalysisBuffers | None:
        """Get the internal analysis buffers."""
        return self._core.buffers
