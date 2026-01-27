"""Streaming analysis engine with compositor and exporters."""

from __future__ import annotations

import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import TYPE_CHECKING, Callable

from trdrop.compositor.base import Compositor
from trdrop.compositor.types import CompositorOutput
from trdrop.export.base import StreamingExporter
from trdrop.export.streaming_video import StreamingVideoExporter
from trdrop.interfaces.mappable import Mappable
from trdrop.interfaces.source import FrameSource
from trdrop.profiling import get_profiler
from trdrop.profiling.profiler import FrameProfile
from trdrop.types.frames import FramePair
from trdrop.types.metrics import FrameMetrics

if TYPE_CHECKING:
    from trdrop.config import FrameLayout, PresetConfig

logger = logging.getLogger(__name__)


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
        synchronous: bool = False,
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
        self._synchronous = synchronous

        # Terminate at shortest source (all sources must provide frame)
        frame_counts = [s.total_frames for s in sources]
        self._total_frames = min(frame_counts)

        # Warn if sources have different lengths
        if len(set(frame_counts)) > 1:
            logger.warning(
                "Video sources have different frame counts: %s. "
                "Processing will stop at frame %d (shortest source).",
                frame_counts,
                self._total_frames,
            )

    @property
    def layout(self) -> FrameLayout | None:
        """Frame layout from compositor, if available."""
        return getattr(self._compositor, 'layout', None)

    @property
    def config(self) -> PresetConfig | None:
        """Config from compositor, if available."""
        return getattr(self._compositor, 'config', None)

    @property
    def total_frames(self) -> int:
        """Total number of frames to process."""
        return self._total_frames

    def run(self) -> None:
        """Run the streaming pipeline to completion."""
        profiler = get_profiler()
        profiler.start_run()

        # Open all exporters
        for exporter in self._exporters:
            exporter.open()

        # Capture encoder info for profiling
        for exporter in self._exporters:
            if isinstance(exporter, StreamingVideoExporter):
                hw_tag = "HW" if exporter.is_hardware_encoder else "SW"
                profiler.set_metadata("Video Encoder", f"{exporter.codec} ({hw_tag})")
                break

        try:
            self._run_loop()
        finally:
            # Close all exporters
            for exporter in self._exporters:
                exporter.close()

            profiler.end_run()

    def _run_loop(self) -> None:
        """Main processing loop."""
        source_iters = [iter(s) for s in self._sources]
        export_future: Future[None] | None = None
        profiler = get_profiler()

        with ThreadPoolExecutor(max_workers=self._analyzer_workers) as pool:
            for frame_idx in range(self._total_frames - 1):  # -1 because pairs
                profiler.start_frame(frame_idx)

                # 1. Pull frame pairs from all sources (parallel)
                t0 = time.perf_counter()
                pairs = self._read_parallel(pool, source_iters)
                if pairs is None:
                    break
                profiler.add_timing("read_total", (time.perf_counter() - t0) * 1000)
                profiler.mark_timestamp("read_end")

                # 2. Analyze all videos in parallel
                t0 = time.perf_counter()
                results = self._analyze_parallel(pool, pairs)
                profiler.add_timing("analysis_total", (time.perf_counter() - t0) * 1000)
                profiler.mark_timestamp("analysis_end")

                # 3. Wait for previous export (protects compositor buffer)
                if export_future is not None:
                    export_future.result()

                # 4. Compositor processes
                t0 = time.perf_counter()
                output = self._compositor.process(pairs, results)
                profiler.add_timing("compositor_total", (time.perf_counter() - t0) * 1000)
                profiler.mark_timestamp("compositor_end")

                # 5. Release source buffers
                for pair in pairs:
                    pair.release()

                # 6. Export (sync or async)
                # Capture frame profile ref for async timestamp recording
                current_profile = getattr(profiler, 'current_frame', None)
                if self._synchronous:
                    self._export_frame(output, current_profile)
                    profiler.mark_timestamp("export_end")
                else:
                    export_future = pool.submit(self._export_frame, output, current_profile)

                profiler.end_frame()

                # Progress callback
                if self._on_frame is not None:
                    self._on_frame(frame_idx, self._total_frames - 1)

        # Wait for final export
        if export_future is not None:
            export_future.result()

        # Close sources
        for source in self._sources:
            source.close()

    def _read_parallel(
        self,
        pool: ThreadPoolExecutor,
        source_iters: list,
    ) -> list[FramePair] | None:
        """Read frame pairs from all sources in parallel."""
        if len(source_iters) == 1:
            # Single source: no need for thread overhead
            try:
                return [next(source_iters[0])]
            except StopIteration:
                return None

        # Multiple sources: read in parallel
        futures: list[Future[FramePair]] = []
        for it in source_iters:
            futures.append(pool.submit(next, it))

        try:
            return [f.result() for f in futures]
        except StopIteration:
            return None

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

    def _export_frame(
        self, output: CompositorOutput, frame_profile: FrameProfile | None = None
    ) -> None:
        """Write frame to all exporters."""
        for exporter in self._exporters:
            exporter.write_frame(output)
        # Record export end timestamp for async overlap calculation
        if frame_profile is not None:
            frame_profile.export_end_ts = time.perf_counter()
