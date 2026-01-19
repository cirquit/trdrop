"""Analysis metrics with monoid structure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


def _merge_field(a: T | None, b: T | None, field_name: str) -> T | None:
    """Merge two optional values. Non-None wins. Both non-None is an error."""
    if a is None:
        return b
    if b is None:
        return a
    raise ValueError(f"Conflicting values for '{field_name}': {a} vs {b}")


@dataclass(frozen=True, slots=True)
class FrameMetrics:
    """
    Analysis metrics for a single frame.

    Monoid structure for composing partial results:
    - Identity: FrameMetrics.empty(frame_index)
    - Operation: + merges non-None fields (conflicts raise ValueError)

    Each Mappable analyzer fills only its own fields.
    The engine folds all partial results with +.
    """

    frame_index: int

    # Duplicate detection
    is_duplicate: bool | None = None
    diff_ratio: float | None = None

    # Tear detection (future)
    tear_rows: tuple[int, ...] | None = None

    # Timing analysis (future)
    frame_time_ms: float | None = None

    @classmethod
    def empty(cls, frame_index: int) -> FrameMetrics:
        """Monoid identity element."""
        return cls(frame_index=frame_index)

    def __add__(self, other: FrameMetrics) -> FrameMetrics:
        """
        Combine two partial FrameMetrics (monoid operation).

        Raises:
            ValueError: If frame_index differs or same field filled by both.
        """
        if self.frame_index != other.frame_index:
            raise ValueError(
                f"Cannot combine metrics for different frames: "
                f"{self.frame_index} vs {other.frame_index}"
            )

        return FrameMetrics(
            frame_index=self.frame_index,
            is_duplicate=_merge_field(self.is_duplicate, other.is_duplicate, "is_duplicate"),
            diff_ratio=_merge_field(self.diff_ratio, other.diff_ratio, "diff_ratio"),
            tear_rows=_merge_field(self.tear_rows, other.tear_rows, "tear_rows"),
            frame_time_ms=_merge_field(self.frame_time_ms, other.frame_time_ms, "frame_time_ms"),
        )
