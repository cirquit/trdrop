"""Streaming analysis engine with compositor and exporters."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable

from trdrop.compositor.base import Compositor
from trdrop.export.base import StreamingExporter
from trdrop.interfaces.mappable import Mappable
from trdrop.interfaces.source import FrameSource
from trdrop.types.frames import FramePair
from trdrop.types.metrics import FrameMetrics


class StreamingEngine:
    """
    Streaming analysis engine with pipelined execution.

    Processes all video sources in lockstep (zip-like), running analysis
    in parallel across videos, then compositing and exporting.

    Execution model per frame:
        1. Pull frame pairs from all sources
        2. Analyze all videos in parallel → list[FrameMetrics]
        3. Wait for previous export to complete (protects compositor buffer)
        4. Compositor processes pairs + results → CompositorOutput
        5. Release source buffers (enables prefetch)
        6. Submit export async (overlaps with next frame's read/analyze)

    Memory model:
        - Engine holds no copies, just references
        - Sources own frame buffers (released after compositor)
        - Compositor owns output buffer (reused each frame)
        - Exporters read from compositor buffer, write to files
    """

    def __init__(
        self,
        sources: list[FrameSource],
        analyzers: list[Mappable[FramePair, FrameMetrics]],
        compositor: Compositor,
        exporters: list[StreamingExporter],
        *,
        analyzer_workers: int | None = None,
        on_frame: Callable[[int, int], None] | None = None,
    ) -> None:
        """
        Args:
            sources: Frame sources for each video (same frame count expected)
            analyzers: Analyzers to run on each video's frame pair
            compositor: Compositor for combining frames and metrics
            exporters: Streaming exporters (opened/closed by engine)
            analyzer_workers: Thread pool size for parallel analysis
            on_frame: Optional callback(frame_idx, total_frames) for progress
        """
        if not sources:
            raise ValueError("At least one source required")

        self._sources = sources
        self._analyzers = analyzers
        self._compositor = compositor
        self._exporters = exporters
        self._analyzer_workers = analyzer_workers
        self._on_frame = on_frame

        # All sources should have same frame count for lockstep
        self._total_frames = min(s.total_frames for s in sources)

    def run(self) -> None:
        """Run the streaming pipeline to completion."""
        # Open all exporters
        for exporter in self._exporters:
            exporter.open()

        try:
            self._run_loop()
        finally:
            # Close all exporters
            for exporter in self._exporters:
                exporter.close()

    def _run_loop(self) -> None:
        """Main processing loop."""
        source_iters = [iter(s) for s in self._sources]
        export_future: Future[None] | None = None

        with ThreadPoolExecutor(max_workers=self._analyzer_workers) as pool:
            for frame_idx in range(self._total_frames - 1):  # -1 because pairs
                # 1. Pull frame pairs from all sources
                pairs: list[FramePair] = []
                try:
                    for it in source_iters:
                        pairs.append(next(it))
                except StopIteration:
                    break

                # 2. Analyze all videos in parallel
                results = self._analyze_parallel(pool, pairs)

                # 3. Wait for previous export (protects compositor buffer)
                if export_future is not None:
                    export_future.result()

                # 4. Compositor processes
                output = self._compositor.process(pairs, results)

                # 5. Release source buffers
                for pair in pairs:
                    pair.release()

                # 6. Submit export async
                export_future = pool.submit(self._export_frame, output)

                # Progress callback
                if self._on_frame is not None:
                    self._on_frame(frame_idx, self._total_frames - 1)

        # Wait for final export
        if export_future is not None:
            export_future.result()

        # Close sources
        for source in self._sources:
            source.close()

    def _analyze_parallel(
        self,
        pool: ThreadPoolExecutor,
        pairs: list[FramePair],
    ) -> list[FrameMetrics]:
        """Run analyzers on all frame pairs in parallel."""
        futures: list[Future[FrameMetrics]] = []

        for pair in pairs:
            # Each video's frame analyzed by all analyzers
            future = pool.submit(self._analyze_single, pair)
            futures.append(future)

        return [f.result() for f in futures]

    def _analyze_single(self, pair: FramePair) -> FrameMetrics:
        """Run all analyzers on a single frame pair, fold results."""
        if not self._analyzers:
            return FrameMetrics.empty(pair.frame_index)

        result = FrameMetrics.empty(pair.frame_index)
        for analyzer in self._analyzers:
            partial = analyzer.map(pair)
            result = result + partial

        return result

    def _export_frame(self, output: CompositorOutput) -> None:
        """Write frame to all exporters."""
        for exporter in self._exporters:
            exporter.write_frame(output)
