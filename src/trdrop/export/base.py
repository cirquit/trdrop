"""Base interface for streaming exporters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from trdrop.compositor.types import AggregatedMetrics, CompositorOutput


class StreamingExporter(ABC):
    """Interface for exporters that write incrementally.

    Lifecycle:
    1. open() - called once at start, opens file handle
    2. write_frame() - called per frame with compositor output
    3. close() - called at end, flushes and closes

    Exporters own their file handles and must be resilient to
    crashes (flush frequently for partial results).
    """

    @abstractmethod
    def open(self) -> None:
        """Open file handle and write any header."""

    @abstractmethod
    def write_frame(self, output: CompositorOutput) -> None:
        """Write a single frame's data.

        Args:
            output: Compositor output with frame and aggregated metrics.
                    The frame buffer is owned by compositor and may be
                    reused after this call returns.
        """

    @abstractmethod
    def close(self) -> None:
        """Flush and close file handle."""

    @property
    @abstractmethod
    def path(self) -> Path:
        """Output file path."""

    def __enter__(self) -> StreamingExporter:
        self.open()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()
