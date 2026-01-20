"""Fixed-size ring buffer for O(1) windowed statistics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import numpy as np


@dataclass(frozen=True, slots=True)
class RingBufferSnapshot:
    """Immutable snapshot of RingBuffer state for seek/restore."""

    data: bytes  # Numpy array as bytes
    dtype: str   # Numpy dtype string
    size: int
    head: int
    count: int
    sum: float


class RingBuffer:
    """Fixed-size circular buffer for windowed computations.

    Pre-allocates a numpy array of fixed size. Supports O(1) push
    and O(1) sum/mean operations via running totals.

    Iteration yields values oldest-to-newest, suitable for plotting.

    Example:
        buf = RingBuffer(size=60, dtype=np.float32)
        buf.push(1.0)
        buf.push(0.0)
        print(buf.sum())   # 1.0
        print(buf.mean())  # 0.5
        print(list(buf))   # [1.0, 0.0]
    """

    __slots__ = ("_data", "_size", "_head", "_count", "_sum")

    def __init__(self, size: int, dtype: np.dtype | type = np.float64) -> None:
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")

        self._data = np.zeros(size, dtype=dtype)
        self._size = size
        self._head = 0
        self._count = 0
        self._sum: float = 0.0

    def push(self, value: float) -> None:
        """Add a value, evicting oldest if full."""
        if self._count == self._size:
            # Evict oldest value from running sum
            self._sum -= float(self._data[self._head])
        else:
            self._count += 1

        self._data[self._head] = value
        self._sum += value
        self._head = (self._head + 1) % self._size

    def sum(self) -> float:
        """O(1) sum of values in buffer."""
        return self._sum

    def mean(self) -> float:
        """O(1) mean of values in buffer."""
        if self._count == 0:
            return 0.0
        return self._sum / self._count

    def clear(self) -> None:
        """Reset buffer to empty state."""
        self._data.fill(0)
        self._head = 0
        self._count = 0
        self._sum = 0.0

    def prefill(self, value: float = 0.0) -> None:
        """Fill buffer to capacity with a value.

        Used to initialize the buffer as "full" for algorithms that
        need a fixed-size window from the start (e.g., FPS calculation
        where FPS = sum of buffer).
        """
        self._data.fill(value)
        self._head = 0
        self._count = self._size
        self._sum = value * self._size

    @property
    def count(self) -> int:
        """Number of values currently in buffer."""
        return self._count

    @property
    def size(self) -> int:
        """Maximum capacity of buffer."""
        return self._size

    @property
    def is_full(self) -> bool:
        """True if buffer is at capacity."""
        return self._count == self._size

    def __len__(self) -> int:
        """Number of values currently in buffer."""
        return self._count

    def __iter__(self) -> Iterator[float]:
        """Iterate values oldest-to-newest."""
        if self._count == 0:
            return

        if self._count < self._size:
            # Not full: elements are at 0.._count-1
            for i in range(self._count):
                yield float(self._data[i])
        else:
            # Full: oldest is at _head, wrap around
            for i in range(self._size):
                idx = (self._head + i) % self._size
                yield float(self._data[idx])

    def __getitem__(self, index: int) -> float:
        """Get value by index (0 = oldest, -1 = newest)."""
        if self._count == 0:
            raise IndexError("buffer is empty")

        if index < 0:
            index = self._count + index

        if index < 0 or index >= self._count:
            raise IndexError(f"index {index} out of range for buffer with {self._count} elements")

        if self._count < self._size:
            # Not full: direct indexing
            return float(self._data[index])
        else:
            # Full: offset from _head (oldest)
            actual_idx = (self._head + index) % self._size
            return float(self._data[actual_idx])

    def snapshot(self) -> RingBufferSnapshot:
        """Create an immutable snapshot of the current state.

        Used for seeking in interactive mode - capture state at frame N,
        restore later when seeking back to frame N.
        """
        return RingBufferSnapshot(
            data=self._data.tobytes(),
            dtype=str(self._data.dtype),
            size=self._size,
            head=self._head,
            count=self._count,
            sum=self._sum,
        )

    def restore(self, snapshot: RingBufferSnapshot) -> None:
        """Restore state from a snapshot.

        Args:
            snapshot: Previously captured snapshot

        Raises:
            ValueError: If snapshot size doesn't match buffer size
        """
        if snapshot.size != self._size:
            raise ValueError(
                f"Snapshot size {snapshot.size} doesn't match buffer size {self._size}"
            )

        self._data = np.frombuffer(snapshot.data, dtype=snapshot.dtype).copy()
        self._head = snapshot.head
        self._count = snapshot.count
        self._sum = snapshot.sum

    @classmethod
    def from_snapshot(cls, snapshot: RingBufferSnapshot) -> "RingBuffer":
        """Create a new RingBuffer from a snapshot."""
        buf = cls(size=snapshot.size, dtype=np.dtype(snapshot.dtype))
        buf.restore(snapshot)
        return buf
