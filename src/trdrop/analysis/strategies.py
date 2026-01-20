"""Duplicate detection strategies for performance comparison.

Each strategy implements the same interface:
    compare(prev, curr, threshold) -> (is_duplicate, diff_ratio)

Strategies:
    - full: Compare all pixels (baseline)
    - stride_2x2: Every 2nd pixel in both dimensions (4x fewer)
    - stride_4x4: Every 4th pixel (16x fewer)
    - rows_2: Every 2nd row (2x fewer)
    - rows_4: Every 4th row (4x fewer)
    - numba_full: JIT-compiled full comparison
    - numba_stride_4x4: JIT-compiled with 4x4 stride
"""

from __future__ import annotations

from typing import Protocol

import numpy as np

# Luminance coefficients
_LUMA_R: float = 0.299
_LUMA_G: float = 0.587
_LUMA_B: float = 0.114


class CompareStrategy(Protocol):
    """Protocol for comparison strategies."""

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int,
        duplicate_threshold: float,
    ) -> tuple[bool, float]:
        """Compare two frames.

        Returns:
            (is_duplicate, diff_ratio)
        """
        ...


def _compare_arrays(
    prev: np.ndarray,
    curr: np.ndarray,
    pixel_threshold: int,
    duplicate_threshold: float,
) -> tuple[bool, float]:
    """Core comparison logic for numpy arrays."""
    # Grayscale conversion
    gray_a = (
        _LUMA_R * prev[..., 0] +
        _LUMA_G * prev[..., 1] +
        _LUMA_B * prev[..., 2]
    )
    gray_b = (
        _LUMA_R * curr[..., 0] +
        _LUMA_G * curr[..., 1] +
        _LUMA_B * curr[..., 2]
    )

    # Difference
    diff = np.abs(gray_b - gray_a)
    diff_pixels = np.count_nonzero(diff > pixel_threshold)
    total_pixels = gray_a.shape[0] * gray_a.shape[1]

    diff_ratio = diff_pixels / total_pixels
    is_duplicate = diff_ratio < duplicate_threshold

    return is_duplicate, diff_ratio


class FullCompare:
    """Compare all pixels (baseline)."""

    name = "full"

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> tuple[bool, float]:
        return _compare_arrays(prev, curr, pixel_threshold, duplicate_threshold)


class Stride2x2Compare:
    """Compare every 2nd pixel in both dimensions (4x fewer pixels)."""

    name = "stride_2x2"

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> tuple[bool, float]:
        return _compare_arrays(
            prev[::2, ::2],
            curr[::2, ::2],
            pixel_threshold,
            duplicate_threshold,
        )


class Stride4x4Compare:
    """Compare every 4th pixel in both dimensions (16x fewer pixels)."""

    name = "stride_4x4"

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> tuple[bool, float]:
        return _compare_arrays(
            prev[::4, ::4],
            curr[::4, ::4],
            pixel_threshold,
            duplicate_threshold,
        )


class Rows2Compare:
    """Compare every 2nd row (2x fewer pixels)."""

    name = "rows_2"

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> tuple[bool, float]:
        return _compare_arrays(
            prev[::2, :],
            curr[::2, :],
            pixel_threshold,
            duplicate_threshold,
        )


class Rows4Compare:
    """Compare every 4th row (4x fewer pixels)."""

    name = "rows_4"

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> tuple[bool, float]:
        return _compare_arrays(
            prev[::4, :],
            curr[::4, :],
            pixel_threshold,
            duplicate_threshold,
        )


# Numba JIT versions - only imported if numba is available
_numba_available = False
try:
    from numba import jit
    _numba_available = True

    @jit(nopython=True, cache=True)
    def _numba_compare_full(
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int,
    ) -> tuple[int, int]:
        """JIT-compiled full pixel comparison."""
        h, w = prev.shape[0], prev.shape[1]
        diff_count = 0

        for y in range(h):
            for x in range(w):
                # Inline grayscale
                gray_a = (
                    0.299 * prev[y, x, 0] +
                    0.587 * prev[y, x, 1] +
                    0.114 * prev[y, x, 2]
                )
                gray_b = (
                    0.299 * curr[y, x, 0] +
                    0.587 * curr[y, x, 1] +
                    0.114 * curr[y, x, 2]
                )
                if abs(gray_b - gray_a) > pixel_threshold:
                    diff_count += 1

        return diff_count, h * w

    @jit(nopython=True, cache=True)
    def _numba_compare_stride(
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int,
        stride: int,
    ) -> tuple[int, int]:
        """JIT-compiled strided comparison."""
        h, w = prev.shape[0], prev.shape[1]
        diff_count = 0
        total = 0

        for y in range(0, h, stride):
            for x in range(0, w, stride):
                gray_a = (
                    0.299 * prev[y, x, 0] +
                    0.587 * prev[y, x, 1] +
                    0.114 * prev[y, x, 2]
                )
                gray_b = (
                    0.299 * curr[y, x, 0] +
                    0.587 * curr[y, x, 1] +
                    0.114 * curr[y, x, 2]
                )
                if abs(gray_b - gray_a) > pixel_threshold:
                    diff_count += 1
                total += 1

        return diff_count, total

    @jit(nopython=True, cache=True)
    def _numba_compare_early_exit(
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int,
        exit_threshold: int,
    ) -> tuple[int, int]:
        """JIT-compiled with early exit when enough differences found."""
        h, w = prev.shape[0], prev.shape[1]
        diff_count = 0
        total = h * w

        for y in range(h):
            for x in range(w):
                gray_a = (
                    0.299 * prev[y, x, 0] +
                    0.587 * prev[y, x, 1] +
                    0.114 * prev[y, x, 2]
                )
                gray_b = (
                    0.299 * curr[y, x, 0] +
                    0.587 * curr[y, x, 1] +
                    0.114 * curr[y, x, 2]
                )
                if abs(gray_b - gray_a) > pixel_threshold:
                    diff_count += 1
                    if diff_count >= exit_threshold:
                        return diff_count, total

        return diff_count, total

except ImportError:
    pass


class NumbaFullCompare:
    """JIT-compiled full comparison."""

    name = "numba_full"

    def __init__(self) -> None:
        if not _numba_available:
            raise RuntimeError("numba not installed")
        self._warmed_up = False

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> tuple[bool, float]:
        # Warm up JIT on first call
        if not self._warmed_up:
            _numba_compare_full(prev[:10, :10], curr[:10, :10], pixel_threshold)
            self._warmed_up = True

        diff_pixels, total_pixels = _numba_compare_full(prev, curr, pixel_threshold)
        diff_ratio = diff_pixels / total_pixels
        return diff_ratio < duplicate_threshold, diff_ratio


class NumbaStride4x4Compare:
    """JIT-compiled with 4x4 stride."""

    name = "numba_stride_4x4"

    def __init__(self) -> None:
        if not _numba_available:
            raise RuntimeError("numba not installed")
        self._warmed_up = False

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> tuple[bool, float]:
        if not self._warmed_up:
            _numba_compare_stride(prev[:10, :10], curr[:10, :10], pixel_threshold, 4)
            self._warmed_up = True

        diff_pixels, total_pixels = _numba_compare_stride(prev, curr, pixel_threshold, 4)
        diff_ratio = diff_pixels / total_pixels
        return diff_ratio < duplicate_threshold, diff_ratio


class NumbaEarlyExitCompare:
    """JIT-compiled with early exit optimization."""

    name = "numba_early_exit"

    def __init__(self) -> None:
        if not _numba_available:
            raise RuntimeError("numba not installed")
        self._warmed_up = False

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        pixel_threshold: int = 10,
        duplicate_threshold: float = 0.01,
    ) -> tuple[bool, float]:
        if not self._warmed_up:
            _numba_compare_early_exit(prev[:10, :10], curr[:10, :10], pixel_threshold, 10)
            self._warmed_up = True

        total_pixels = prev.shape[0] * prev.shape[1]
        exit_threshold = int(total_pixels * duplicate_threshold) + 1

        diff_pixels, total_pixels = _numba_compare_early_exit(
            prev, curr, pixel_threshold, exit_threshold
        )
        diff_ratio = diff_pixels / total_pixels
        return diff_ratio < duplicate_threshold, diff_ratio


def get_all_strategies() -> list[CompareStrategy]:
    """Get all available comparison strategies."""
    strategies: list[CompareStrategy] = [
        FullCompare(),
        Stride2x2Compare(),
        Stride4x4Compare(),
        Rows2Compare(),
        Rows4Compare(),
    ]

    if _numba_available:
        strategies.extend([
            NumbaFullCompare(),
            NumbaStride4x4Compare(),
            NumbaEarlyExitCompare(),
        ])

    return strategies


def get_strategy(name: str) -> CompareStrategy:
    """Get a strategy by name."""
    for s in get_all_strategies():
        if s.name == name:
            return s
    raise ValueError(f"Unknown strategy: {name}")
