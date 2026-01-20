"""Performance profiler for pipeline timing analysis.

Enable profiling by setting the TRDROP_PROFILE environment variable:
    TRDROP_PROFILE=1                    # Output to ./trdrop_profile.csv
    TRDROP_PROFILE=/path/to/output.csv  # Output to custom path

The profiler tracks per-frame timing for each pipeline stage with:
    - Per-frame timings in CSV
    - Summary with mean ± std for all stages
    - Pipeline overlap analysis (parallel execution efficiency)
    - Compositor breakdown for optimization insights
"""

from __future__ import annotations

import csv
import math
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Iterator

# Environment variable to enable profiling
PROFILE_ENV_VAR = "TRDROP_PROFILE"


def _std(values: list[float], mean: float) -> float:
    """Compute standard deviation."""
    if len(values) < 2:
        return 0.0
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


@dataclass
class FrameProfile:
    """Timing data for a single frame."""

    frame_index: int = -1

    # Absolute timestamps (for overlap calculation)
    frame_start_ts: float = 0.0
    read_end_ts: float = 0.0
    analysis_end_ts: float = 0.0
    compositor_end_ts: float = 0.0
    export_end_ts: float = 0.0

    # Frame reading
    read_decode_ms: float = 0.0
    read_total_ms: float = 0.0

    # Analysis
    analysis_duplicate_ms: float = 0.0
    analysis_total_ms: float = 0.0

    # Compositor - high level
    compositor_compose_ms: float = 0.0
    compositor_overlay_ms: float = 0.0
    compositor_total_ms: float = 0.0

    # Compositor - overlay breakdown
    overlay_fps_text_ms: float = 0.0
    overlay_plot_background_ms: float = 0.0
    overlay_plot_grid_ms: float = 0.0
    overlay_plot_axes_ms: float = 0.0
    overlay_plot_line_ms: float = 0.0
    overlay_plot_trail_ms: float = 0.0
    overlay_plot_labels_ms: float = 0.0
    overlay_plot_title_ms: float = 0.0

    # Export
    export_video_convert_ms: float = 0.0
    export_video_encode_ms: float = 0.0
    export_video_total_ms: float = 0.0
    export_csv_ms: float = 0.0

    # Total frame time (wall clock for this frame's work)
    frame_total_ms: float = 0.0


@dataclass
class StageStats:
    """Statistics for a single stage."""

    name: str
    mean_ms: float
    std_ms: float
    min_ms: float
    max_ms: float
    pct_of_total: float


@dataclass
class OverlapStats:
    """Pipeline overlap/parallelism statistics."""

    # Theoretical sequential time (sum of all stages)
    theoretical_sequential_ms: float = 0.0
    # Actual wall clock time
    actual_wall_ms: float = 0.0
    # Overlap achieved (theoretical - actual)
    overlap_ms: float = 0.0
    # Overlap percentage
    overlap_pct: float = 0.0

    # Per-stage overlap with previous export
    read_during_prev_export_pct: float = 0.0
    analysis_during_prev_export_pct: float = 0.0


class NullProfiler:
    """No-op profiler when profiling is disabled."""

    @property
    def enabled(self) -> bool:
        return False

    def start_run(self) -> None:
        pass

    def end_run(self) -> None:
        pass

    def start_frame(self, frame_index: int) -> None:
        pass

    def end_frame(self) -> None:
        pass

    def mark_timestamp(self, name: str) -> None:
        pass

    @contextmanager
    def time(self, stage: str) -> Iterator[None]:
        yield

    def add_timing(self, stage: str, duration_ms: float) -> None:
        pass


class Profiler:
    """Performance profiler that tracks per-frame pipeline timing.

    Use context managers or explicit timing methods to measure stages:

        profiler.start_frame(idx)
        with profiler.time("read_total"):
            # frame reading code
        profiler.mark_timestamp("read_end")
        with profiler.time("analysis_duplicate"):
            # analysis code
        profiler.end_frame()

    On end_run(), writes all timing data to CSV and summary.
    """

    def __init__(self, output_path: str | Path) -> None:
        self._output_path = Path(output_path)
        self._frames: list[FrameProfile] = []
        self._current_frame: FrameProfile | None = None
        self._run_start: float = 0.0
        self._run_end: float = 0.0
        self._frame_start: float = 0.0

    @property
    def enabled(self) -> bool:
        return True

    @property
    def output_path(self) -> Path:
        return self._output_path

    @property
    def current_frame(self) -> FrameProfile | None:
        """Get current frame profile for async timestamp recording."""
        return self._current_frame

    def start_run(self) -> None:
        """Mark start of processing run."""
        self._run_start = time.perf_counter()
        self._frames = []

    def end_run(self) -> None:
        """Mark end of processing run and write CSV."""
        self._run_end = time.perf_counter()
        self._write_csv()
        self._write_summary()

    def start_frame(self, frame_index: int) -> None:
        """Start timing for a new frame."""
        now = time.perf_counter()
        self._current_frame = FrameProfile(
            frame_index=frame_index,
            frame_start_ts=now,
        )
        self._frame_start = now

    def end_frame(self) -> None:
        """End timing for current frame and record it."""
        if self._current_frame is not None:
            elapsed = (time.perf_counter() - self._frame_start) * 1000
            self._current_frame.frame_total_ms = elapsed
            self._frames.append(self._current_frame)
            self._current_frame = None

    def mark_timestamp(self, name: str) -> None:
        """Record an absolute timestamp for overlap analysis."""
        if self._current_frame is not None:
            ts_attr = f"{name}_ts"
            if hasattr(self._current_frame, ts_attr):
                setattr(self._current_frame, ts_attr, time.perf_counter())

    @contextmanager
    def time(self, stage: str) -> Iterator[None]:
        """Context manager to time a stage.

        Args:
            stage: Stage name (without _ms suffix), e.g., "read_decode"
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.add_timing(stage, elapsed_ms)

    def add_timing(self, stage: str, duration_ms: float) -> None:
        """Add timing for a stage to current frame.

        Args:
            stage: Stage name (without _ms suffix)
            duration_ms: Duration in milliseconds
        """
        if self._current_frame is not None:
            attr = f"{stage}_ms"
            if hasattr(self._current_frame, attr):
                # Accumulate (for stages called multiple times)
                current = getattr(self._current_frame, attr)
                setattr(self._current_frame, attr, current + duration_ms)

    def _compute_stage_stats(
        self, name: str, values: list[float], total_sum: float
    ) -> StageStats:
        """Compute statistics for a stage."""
        if not values:
            return StageStats(name, 0, 0, 0, 0, 0)

        mean = sum(values) / len(values)
        std = _std(values, mean)
        min_val = min(values)
        max_val = max(values)
        pct = (sum(values) / total_sum * 100) if total_sum > 0 else 0

        return StageStats(name, mean, std, min_val, max_val, pct)

    def _compute_overlap_stats(self) -> OverlapStats:
        """Compute pipeline overlap/parallelism statistics."""
        if len(self._frames) < 2:
            return OverlapStats()

        # Sum of all individual stage times (theoretical sequential)
        theoretical = sum(
            f.read_total_ms + f.analysis_total_ms + f.compositor_total_ms
            + f.export_video_total_ms + f.export_csv_ms
            for f in self._frames
        )

        # Actual wall clock time
        actual = (self._run_end - self._run_start) * 1000

        overlap = theoretical - actual
        overlap_pct = (overlap / theoretical * 100) if theoretical > 0 else 0

        # Calculate how much read/analysis overlaps with previous export
        # by looking at timestamps
        read_overlap_total = 0.0
        analysis_overlap_total = 0.0
        read_total = 0.0
        analysis_total = 0.0

        for i in range(1, len(self._frames)):
            curr = self._frames[i]
            prev = self._frames[i - 1]

            # Previous export ends at prev.export_end_ts
            # Current read starts at curr.frame_start_ts, ends at curr.read_end_ts
            # Current analysis ends at curr.analysis_end_ts

            if prev.export_end_ts > 0 and curr.read_end_ts > 0:
                read_duration = curr.read_total_ms
                read_total += read_duration

                # Overlap = time when current read runs while prev export running
                # prev export runs from prev.compositor_end_ts to prev.export_end_ts
                prev_export_start = prev.compositor_end_ts
                prev_export_end = prev.export_end_ts
                curr_read_start = curr.frame_start_ts
                curr_read_end = curr.read_end_ts

                if prev_export_end > curr_read_start:
                    # There is overlap
                    overlap_start = max(prev_export_start, curr_read_start)
                    overlap_end = min(prev_export_end, curr_read_end)
                    if overlap_end > overlap_start:
                        read_overlap_total += (overlap_end - overlap_start) * 1000

            if prev.export_end_ts > 0 and curr.analysis_end_ts > 0:
                analysis_duration = curr.analysis_total_ms
                analysis_total += analysis_duration

                prev_export_start = prev.compositor_end_ts
                prev_export_end = prev.export_end_ts
                curr_analysis_start = (
                    curr.read_end_ts if curr.read_end_ts > 0 else curr.frame_start_ts
                )
                curr_analysis_end = curr.analysis_end_ts

                if prev_export_end > curr_analysis_start:
                    overlap_start = max(prev_export_start, curr_analysis_start)
                    overlap_end = min(prev_export_end, curr_analysis_end)
                    if overlap_end > overlap_start:
                        analysis_overlap_total += (overlap_end - overlap_start) * 1000

        read_overlap_pct = (read_overlap_total / read_total * 100) if read_total > 0 else 0
        analysis_overlap_pct = (
            (analysis_overlap_total / analysis_total * 100) if analysis_total > 0 else 0
        )

        return OverlapStats(
            theoretical_sequential_ms=theoretical,
            actual_wall_ms=actual,
            overlap_ms=overlap,
            overlap_pct=overlap_pct,
            read_during_prev_export_pct=read_overlap_pct,
            analysis_during_prev_export_pct=analysis_overlap_pct,
        )

    def _write_csv(self) -> None:
        """Write profiling data to CSV file."""
        if not self._frames:
            return

        self._output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get field names from FrameProfile (exclude timestamps for cleaner CSV)
        all_fields = [f.name for f in fields(FrameProfile)]
        field_names = [f for f in all_fields if not f.endswith("_ts")]

        with open(self._output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()

            for frame in self._frames:
                row = {name: getattr(frame, name) for name in field_names}
                writer.writerow(row)

    def _write_summary(self) -> None:
        """Write detailed summary with stats and overlap analysis."""
        if not self._frames:
            return

        summary_path = self._output_path.with_suffix(".summary.txt")
        n = len(self._frames)
        total_time = self._run_end - self._run_start

        # Collect values for each stage
        stages = {
            "read_decode": [f.read_decode_ms for f in self._frames],
            "read_total": [f.read_total_ms for f in self._frames],
            "analysis_duplicate": [f.analysis_duplicate_ms for f in self._frames],
            "analysis_total": [f.analysis_total_ms for f in self._frames],
            "compositor_compose": [f.compositor_compose_ms for f in self._frames],
            "compositor_overlay": [f.compositor_overlay_ms for f in self._frames],
            "compositor_total": [f.compositor_total_ms for f in self._frames],
            "overlay_fps_text": [f.overlay_fps_text_ms for f in self._frames],
            "overlay_plot_background": [f.overlay_plot_background_ms for f in self._frames],
            "overlay_plot_grid": [f.overlay_plot_grid_ms for f in self._frames],
            "overlay_plot_axes": [f.overlay_plot_axes_ms for f in self._frames],
            "overlay_plot_line": [f.overlay_plot_line_ms for f in self._frames],
            "overlay_plot_trail": [f.overlay_plot_trail_ms for f in self._frames],
            "overlay_plot_labels": [f.overlay_plot_labels_ms for f in self._frames],
            "overlay_plot_title": [f.overlay_plot_title_ms for f in self._frames],
            "export_video_convert": [f.export_video_convert_ms for f in self._frames],
            "export_video_encode": [f.export_video_encode_ms for f in self._frames],
            "export_video_total": [f.export_video_total_ms for f in self._frames],
            "export_csv": [f.export_csv_ms for f in self._frames],
            "frame_total": [f.frame_total_ms for f in self._frames],
        }

        # Total measured time for percentage calculation
        total_measured = sum(
            sum(stages["read_total"]) + sum(stages["analysis_total"])
            + sum(stages["compositor_total"]) + sum(stages["export_video_total"])
            + sum(stages["export_csv"])
            for _ in [1]
        )

        # Compute stats for each stage
        stats = {
            name: self._compute_stage_stats(name, values, total_measured)
            for name, values in stages.items()
        }

        # Compute overlap stats
        overlap = self._compute_overlap_stats()

        with open(summary_path, "w") as f:
            f.write("TRDrop Profiling Summary\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total frames: {n}\n")
            f.write(f"Total time: {total_time:.2f}s\n")
            f.write(f"Average FPS: {n / total_time:.1f}\n\n")

            # Main stages with mean ± std
            f.write("Per-Stage Timing (ms/frame): mean ± std [min, max]\n")
            f.write("-" * 70 + "\n")

            main_stages = [
                ("Read (decode)", "read_decode"),
                ("Read (total)", "read_total"),
                ("Analysis (dup)", "analysis_duplicate"),
                ("Analysis (total)", "analysis_total"),
                ("Compositor (compose)", "compositor_compose"),
                ("Compositor (overlay)", "compositor_overlay"),
                ("Compositor (total)", "compositor_total"),
                ("Export Video (convert)", "export_video_convert"),
                ("Export Video (encode)", "export_video_encode"),
                ("Export Video (total)", "export_video_total"),
                ("Export CSV", "export_csv"),
                ("Frame Total", "frame_total"),
            ]

            for label, key in main_stages:
                s = stats[key]
                f.write(
                    f"  {label:24s} {s.mean_ms:8.3f} ± {s.std_ms:6.3f}  "
                    f"[{s.min_ms:7.3f}, {s.max_ms:8.3f}]\n"
                )

            f.write("\n")

            # Compositor overlay breakdown
            f.write("Compositor Overlay Breakdown (ms/frame): mean ± std\n")
            f.write("-" * 70 + "\n")

            overlay_stages = [
                ("FPS Text", "overlay_fps_text"),
                ("Plot Background", "overlay_plot_background"),
                ("Plot Grid", "overlay_plot_grid"),
                ("Plot Axes", "overlay_plot_axes"),
                ("Plot Line (exact)", "overlay_plot_line"),
                ("Plot Trail (smoothed)", "overlay_plot_trail"),
                ("Plot Labels", "overlay_plot_labels"),
                ("Plot Title", "overlay_plot_title"),
            ]

            overlay_total = 0.0
            for label, key in overlay_stages:
                s = stats[key]
                overlay_total += s.mean_ms
                if s.mean_ms > 0.001:  # Only show non-zero
                    f.write(f"  {label:24s} {s.mean_ms:8.3f} ± {s.std_ms:6.3f}\n")

            f.write(f"  {'─' * 40}\n")
            f.write(f"  {'Overlay Total':24s} {overlay_total:8.3f}\n")

            f.write("\n")

            # Time distribution
            f.write("Time Distribution (% of measured time):\n")
            f.write("-" * 70 + "\n")

            dist_stages = [
                ("Read", "read_total"),
                ("Analysis", "analysis_total"),
                ("Compositor", "compositor_total"),
                ("Export Video", "export_video_total"),
                ("Export CSV", "export_csv"),
            ]

            for label, key in dist_stages:
                s = stats[key]
                bar_len = int(s.pct_of_total / 2)
                bar = "█" * bar_len
                f.write(f"  {label:14s} {s.pct_of_total:5.1f}%  {bar}\n")

            f.write("\n")

            # Pipeline overlap analysis
            f.write("Pipeline Overlap Analysis:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Theoretical sequential time: {overlap.theoretical_sequential_ms:,.1f} ms\n")
            f.write(f"  Actual wall clock time:      {overlap.actual_wall_ms:,.1f} ms\n")
            f.write(
                f"  Time saved by parallelism:   {overlap.overlap_ms:,.1f} ms "
                f"({overlap.overlap_pct:.1f}%)\n"
            )
            f.write("\n")
            f.write("  Stage overlap with previous frame's export:\n")
            f.write(f"    Read overlaps:     {overlap.read_during_prev_export_pct:5.1f}%\n")
            f.write(f"    Analysis overlaps: {overlap.analysis_during_prev_export_pct:5.1f}%\n")

            f.write("\n")

            # Optimization recommendations
            f.write("Optimization Opportunities:\n")
            f.write("-" * 70 + "\n")

            # Find biggest bottleneck
            bottlenecks = [
                (stats["read_total"].mean_ms, "Read", "read_total"),
                (stats["analysis_total"].mean_ms, "Analysis", "analysis_total"),
                (stats["compositor_total"].mean_ms, "Compositor", "compositor_total"),
                (stats["export_video_total"].mean_ms, "Export Video", "export_video"),
            ]
            bottlenecks.sort(reverse=True)

            f.write(
                f"\n  Top bottleneck: {bottlenecks[0][1]} "
                f"({bottlenecks[0][0]:.1f} ms/frame)\n\n"
            )

            # Compositor-specific recommendations
            comp_overlay = stats["compositor_overlay"].mean_ms
            comp_compose = stats["compositor_compose"].mean_ms

            if comp_overlay > comp_compose:
                f.write("  Compositor Analysis:\n")
                f.write(
                    f"    Overlay rendering ({comp_overlay:.1f}ms) > "
                    f"Composition ({comp_compose:.1f}ms)\n"
                )
                f.write("    Consider:\n")

                # Check which overlay component is slowest
                overlay_times = [
                    (stats["overlay_plot_line"].mean_ms, "Plot line drawing"),
                    (stats["overlay_plot_trail"].mean_ms, "Plot smoothed trail"),
                    (stats["overlay_plot_background"].mean_ms, "Plot background"),
                    (stats["overlay_fps_text"].mean_ms, "FPS text rendering"),
                    (stats["overlay_plot_labels"].mean_ms, "Plot labels"),
                    (stats["overlay_plot_grid"].mean_ms, "Plot grid"),
                ]
                overlay_times.sort(reverse=True)

                for time_ms, name in overlay_times[:3]:
                    if time_ms > 0.1:
                        f.write(f"      - {name}: {time_ms:.2f}ms\n")

                f.write("\n    Potential optimizations:\n")
                f.write("      - Cache QPainterPath for plot lines\n")
                f.write("      - Reduce plot data points (downsample history)\n")
                f.write("      - Pre-render static elements (grid, axes)\n")
                f.write("      - Use OpenGL for overlay rendering\n")


# Singleton profiler instance
_profiler: Profiler | NullProfiler | None = None


def get_profiler() -> Profiler | NullProfiler:
    """Get the global profiler instance.

    Returns a NullProfiler (no-op) if TRDROP_PROFILE is not set.
    Returns a Profiler writing to the specified path if TRDROP_PROFILE is set.

    TRDROP_PROFILE=1           → writes to ./trdrop_profile.csv
    TRDROP_PROFILE=/path.csv   → writes to specified path
    """
    global _profiler

    if _profiler is not None:
        return _profiler

    env_value = os.environ.get(PROFILE_ENV_VAR, "")

    if not env_value:
        _profiler = NullProfiler()
    elif env_value == "1":
        _profiler = Profiler("trdrop_profile.csv")
    else:
        _profiler = Profiler(env_value)

    return _profiler


def reset_profiler() -> None:
    """Reset the global profiler instance (for testing)."""
    global _profiler
    _profiler = None
