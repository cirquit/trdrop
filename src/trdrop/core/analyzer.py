"""Frame analysis using numpy (zero-copy operations)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class FrameAnalyzer(Protocol):
    """Protocol for frame analysis implementations."""

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        threshold: int = 10,
    ) -> tuple[bool, float]:
        """
        Compare two frames for duplicate detection.

        Args:
            prev: Previous frame (H, W, 3) uint8
            curr: Current frame (H, W, 3) uint8
            threshold: Pixel difference threshold (0-255)

        Returns:
            (is_duplicate, diff_ratio) where diff_ratio is 0.0-1.0
        """
        ...

    def detect_tears(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        threshold: float = 0.1,
    ) -> list[int]:
        """
        Detect screen tears between frames.

        Args:
            prev: Previous frame (H, W, 3) uint8
            curr: Current frame (H, W, 3) uint8
            threshold: Row difference threshold (0.0-1.0)

        Returns:
            List of row indices where tears detected
        """
        ...


@dataclass(slots=True)
class AnalysisBuffers:
    """Pre-allocated work buffers for frame analysis.

    All buffers are float32 arrays of shape (height, width).
    """

    gray_a: np.ndarray
    gray_b: np.ndarray
    diff: np.ndarray
    row_means: np.ndarray

    @staticmethod
    def allocate(height: int, width: int) -> AnalysisBuffers:
        """Allocate buffers for given frame dimensions."""
        return AnalysisBuffers(
            gray_a=np.empty((height, width), dtype=np.float32),
            gray_b=np.empty((height, width), dtype=np.float32),
            diff=np.empty((height, width), dtype=np.float32),
            row_means=np.empty(height, dtype=np.float32),
        )

    @property
    def shape(self) -> tuple[int, int]:
        return (self.gray_a.shape[0], self.gray_a.shape[1])


# Luminance coefficients for RGB to grayscale conversion
_LUMA_R: float = 0.299
_LUMA_G: float = 0.587
_LUMA_B: float = 0.114


def grayscale_into(rgb: np.ndarray, out: np.ndarray) -> None:
    """Convert RGB to grayscale, writing to pre-allocated buffer.

    Uses standard luminance formula: Y = 0.299*R + 0.587*G + 0.114*B

    Args:
        rgb: Input RGB array of shape (H, W, 3) uint8
        out: Output buffer of shape (H, W) float32
    """
    np.multiply(rgb[..., 0], _LUMA_R, out=out, casting="unsafe")
    out += _LUMA_G * rgb[..., 1]
    out += _LUMA_B * rgb[..., 2]


def compare_chunk(
    chunk_a: np.ndarray,
    chunk_b: np.ndarray,
    gray_a: np.ndarray,
    gray_b: np.ndarray,
    diff: np.ndarray,
    threshold: int,
) -> tuple[int, int]:
    """Compare a chunk of two frames for difference detection.

    This function enables parallel processing by allowing frames to be
    split into horizontal strips that are analyzed independently.

    Args:
        chunk_a: First chunk (H, W, 3) uint8
        chunk_b: Second chunk (H, W, 3) uint8
        gray_a: Pre-allocated grayscale buffer for chunk_a
        gray_b: Pre-allocated grayscale buffer for chunk_b
        diff: Pre-allocated diff buffer
        threshold: Pixel difference threshold (0-255)

    Returns:
        (diff_pixels, total_pixels) for this chunk
    """
    grayscale_into(chunk_a, gray_a)
    grayscale_into(chunk_b, gray_b)

    np.subtract(gray_b, gray_a, out=diff)
    np.abs(diff, out=diff)

    diff_pixels: int = int(np.count_nonzero(diff > threshold))
    total_pixels: int = gray_a.shape[0] * gray_a.shape[1]

    return diff_pixels, total_pixels


def detect_tears_chunk(
    chunk_a: np.ndarray,
    chunk_b: np.ndarray,
    gray_a: np.ndarray,
    gray_b: np.ndarray,
    diff: np.ndarray,
    row_means: np.ndarray,
    threshold: float,
    row_offset: int = 0,
) -> list[int]:
    """Detect tears in a chunk of two frames.

    This function enables parallel processing by allowing frames to be
    split into horizontal strips that are analyzed independently.

    Args:
        chunk_a: First chunk (H, W, 3) uint8
        chunk_b: Second chunk (H, W, 3) uint8
        gray_a: Pre-allocated grayscale buffer
        gray_b: Pre-allocated grayscale buffer
        diff: Pre-allocated diff buffer
        row_means: Pre-allocated row means buffer (H,)
        threshold: Row difference threshold (0.0-1.0)
        row_offset: Offset to add to returned row indices

    Returns:
        List of row indices (with offset) where tears detected
    """
    grayscale_into(chunk_a, gray_a)
    grayscale_into(chunk_b, gray_b)

    np.subtract(gray_b, gray_a, out=diff)
    np.abs(diff, out=diff)

    # Compute row means in-place
    np.mean(diff, axis=1, out=row_means)
    row_means /= 255.0

    # Find transitions
    h: int = chunk_a.shape[0]
    tear_rows: list[int] = []
    prev_high: bool = bool(row_means[0] > threshold)

    for row in range(1, h):
        curr_high: bool = bool(row_means[row] > threshold)
        if curr_high != prev_high:
            tear_rows.append(row + row_offset)
        prev_high = curr_high

    return tear_rows


class NumpyAnalyzer:
    """Frame analyzer using numpy operations with O(1) memory per frame."""

    def __init__(
        self,
        pixel_threshold: int = 10,
        tear_threshold: float = 0.1,
        duplicate_threshold: float = 0.01,
    ) -> None:
        self.pixel_threshold = pixel_threshold
        self.tear_threshold = tear_threshold
        self.duplicate_threshold = duplicate_threshold

        self._buffers: AnalysisBuffers | None = None

    def _ensure_buffers(self, height: int, width: int) -> AnalysisBuffers:
        """Ensure work buffers are allocated for given dimensions."""
        if self._buffers is None or self._buffers.shape != (height, width):
            self._buffers = AnalysisBuffers.allocate(height, width)
        return self._buffers

    def compare(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        threshold: int | None = None,
    ) -> tuple[bool, float]:
        """Compare frames for duplicate detection."""
        if threshold is None:
            threshold = self.pixel_threshold

        h, w = prev.shape[:2]
        buf = self._ensure_buffers(h, w)

        diff_pixels, total_pixels = compare_chunk(
            prev, curr, buf.gray_a, buf.gray_b, buf.diff, threshold
        )

        diff_ratio: float = diff_pixels / total_pixels
        is_duplicate: bool = diff_ratio < self.duplicate_threshold

        return is_duplicate, diff_ratio

    def detect_tears(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        threshold: float | None = None,
    ) -> list[int]:
        """Detect screen tears by analyzing row-by-row differences."""
        if threshold is None:
            threshold = self.tear_threshold

        h, w = prev.shape[:2]
        buf = self._ensure_buffers(h, w)

        return detect_tears_chunk(
            prev, curr, buf.gray_a, buf.gray_b, buf.diff, buf.row_means, threshold
        )

    # Expose buffers for external buffer reuse (e.g., parallel processing)
    @property
    def buffers(self) -> AnalysisBuffers | None:
        return self._buffers
