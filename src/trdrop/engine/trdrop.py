"""TRDrop analysis engine."""

from __future__ import annotations

import copy
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from functools import reduce
from pathlib import Path

from trdrop.interfaces.mappable import Mappable
from trdrop.interfaces.source import FrameSource
from trdrop.types.frames import FramePair
from trdrop.types.metrics import FrameMetrics


@dataclass(frozen=True, slots=True)
class VideoResult:
    """Analysis result for a single video."""

    path: Path
    fps: float
    total_frames: int
    metrics: tuple[FrameMetrics, ...]

    @property
    def unique_frames(self) -> int:
        # First frame is always unique (no comparison)
        first_frame = 1
        unique_compared = sum(1 for m in self.metrics if not m.is_duplicate)
        return first_frame + unique_compared

    @property
    def duplicate_frames(self) -> int:
        return sum(1 for m in self.metrics if m.is_duplicate)

    @property
    def duration_sec(self) -> float:
        return self.total_frames / self.fps if self.fps > 0 else 0.0

    @property
    def detected_fps(self) -> float:
        duration = self.duration_sec
        return self.unique_frames / duration if duration > 0 else 0.0


class TrdropEngine:
    """
    Analysis engine with two-level parallelism.

    - Videos processed in parallel
    - Analyzers run in parallel per frame
    """

    def __init__(
        self,
        analyzers: list[Mappable[FramePair, FrameMetrics]],
        *,
        video_workers: int | None = None,
        analyzer_workers: int | None = None,
    ) -> None:
        self._analyzers = analyzers
        self._video_workers = video_workers
        self._analyzer_workers = analyzer_workers

    def run(self, sources: list[tuple[Path, FrameSource]]) -> list[VideoResult]:
        """
        Run analysis on multiple videos in parallel.

        Args:
            sources: List of (path, source) tuples

        Returns:
            List of VideoResult, one per input (same order)
        """
        if not sources:
            return []

        with ThreadPoolExecutor(max_workers=self._video_workers) as pool:
            futures: list[Future[VideoResult]] = [
                pool.submit(self._process_video, path, source)
                for path, source in sources
            ]
            return [f.result() for f in futures]

    def _process_video(self, path: Path, source: FrameSource) -> VideoResult:
        """Process a single video."""
        # Create per-video copies to avoid shared state across video threads
        analyzers = [copy.deepcopy(a) for a in self._analyzers]
        metrics: list[FrameMetrics] = []

        with ThreadPoolExecutor(max_workers=self._analyzer_workers) as pool:
            for pair in source:
                combined = self._analyze_frame(pool, pair, analyzers)
                # Release after analysis (future: after render creates composited buffer)
                # This allows source to recycle buffers while export runs
                pair.release()
                metrics.append(combined)

        source.close()

        return VideoResult(
            path=path,
            fps=source.fps,
            total_frames=source.total_frames,
            metrics=tuple(metrics),
        )

    def _analyze_frame(
        self,
        pool: ThreadPoolExecutor,
        pair: FramePair,
        analyzers: list[Mappable[FramePair, FrameMetrics]],
    ) -> FrameMetrics:
        """Run all analyzers on a frame pair, fold results."""
        if len(analyzers) == 1:
            return analyzers[0].map(pair)

        futures = [pool.submit(analyzer.map, pair) for analyzer in analyzers]
        partials = [f.result() for f in futures]

        return reduce(
            lambda a, b: a + b,
            partials,
            FrameMetrics.empty(pair.frame_index),
        )
