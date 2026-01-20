# TRDrop v2 Architecture

## Overview

TRDrop analyzes video files to detect the actual content framerate by identifying duplicate frames. A video recorded at 30fps but encoded in a 60fps container will have every other frame duplicated - TRDrop detects this pattern.

## Module Structure

```
src/trdrop/
├── types/              # Immutable data types
│   ├── frames.py       # FrameView, FramePair, ReleaseCallback
│   └── metrics.py      # FrameMetrics (monoid)
│
├── interfaces/         # Abstract base classes
│   ├── video.py        # VideoReader
│   ├── source.py       # FrameSource
│   └── mappable.py     # Mappable[In, Out]
│
├── video/              # Video I/O implementations
│   └── reader.py       # PyAVReader(VideoReader)
│
├── source/             # Frame source implementations
│   ├── sequential.py   # SequentialFrameSource
│   ├── prefetching.py  # PrefetchingFrameSource (stub)
│   └── mock.py         # MockFrameSource (testing)
│
├── analysis/           # Frame analysis
│   ├── core.py         # NumpyAnalyzer, AnalysisBuffers
│   └── duplicate.py    # DuplicateDetector(Mappable)
│
├── compositor/         # Frame composition and aggregation
│   ├── base.py         # Compositor ABC
│   ├── simple.py       # SimpleCompositor
│   ├── types.py        # VideoMetrics, AggregatedMetrics, CompositorOutput
│   └── overlay/        # Overlay rendering
│       ├── text.py     # FPSText
│       └── plot.py     # FrameratePlot, FrametimePlot
│
├── engine/             # Orchestration
│   ├── trdrop.py       # TrdropEngine (batch mode)
│   └── streaming.py    # StreamingEngine (pipelined mode)
│
├── export/             # Result export
│   ├── base.py         # StreamingExporter ABC
│   ├── csv.py          # Batch CSV export
│   ├── json.py         # Batch JSON export/import
│   ├── streaming_csv.py    # StreamingCSVExporter
│   └── streaming_video.py  # StreamingVideoExporter
│
├── profiling/          # Performance profiling
│   └── profiler.py     # Profiler, FrameProfile, get_profiler()
│
└── utils/              # Utilities
    └── ringbuffer.py   # O(1) RingBuffer for windowed stats
```

## Execution Models

### StreamingEngine (Primary)

Processes all videos in lockstep with pipelined execution:

```
for frame_idx in range(total_frames):
    pairs = pull_frames(sources)           # All videos, lockstep
    results = analyze_parallel(pairs)      # Parallel across videos

    wait_previous_export()                 # Protect compositor buffer

    output = compositor.process(pairs, results)  # Sync point
    release_all(pairs)                     # Source can recycle buffers

    submit_export_async(output)            # Overlaps with next read/analyze
```

**Pipeline overlap:**
```
Frame N:   [read] [analyze] [composite] [release] [export...........]
Frame N+1:                              [read] [analyze] [wait] [composite] ...
                                                          ↑
                                                   waits for N's export
```

### TrdropEngine (Batch)

Processes videos independently, returns complete results at end. Useful for batch analysis without streaming output.

## FPS Estimation

TRDrop's core feature is estimating the actual content framerate by detecting duplicate frames.

### The Problem

A game running at 30fps recorded in a 60fps container produces a video where every other frame is a duplicate. The video file reports 60fps, but the actual content only changes 30 times per second.

### The Algorithm

For each frame pair (prev, curr):

1. **Compare frames** → `is_duplicate` (boolean)
   - Convert to grayscale, compute pixel-wise difference
   - If < 1% of pixels differ by > threshold → duplicate

2. **Track in ring buffer** → overwrite at circular index with `1.0` (unique) or `0.0` (duplicate)

3. **Calculate windowed FPS**:
   ```
   windowed_fps = sum(ring_buffer)
   ```

### Why Sum, Not Mean?

The buffer is **pre-filled with zeros** and has a fixed size equal to the container FPS (≈1 second of frames). This design choice from TRDrop v1 has important properties:

**Sum-based (v1 algorithm):**
```
Buffer initialized: [0, 0, 0, ..., 0]  (60 zeros)
Frame 1 (dup):  buffer[0] = 0  → sum = 0   → FPS = 0
Frame 2 (uniq): buffer[1] = 1  → sum = 1   → FPS = 1
Frame 3 (dup):  buffer[2] = 0  → sum = 1   → FPS = 1
Frame 4 (uniq): buffer[3] = 1  → sum = 2   → FPS = 2
...
Frame 60:       buffer full    → sum = 30  → FPS = 30 ✓
```

**Mean-based (rejected):**
```
Buffer grows: []
Frame 1 (dup):  [0]        → mean = 0.0  → 60 × 0.0 = 0
Frame 2 (uniq): [0, 1]     → mean = 0.5  → 60 × 0.5 = 30  ← oscillates!
Frame 3 (dup):  [0, 1, 0]  → mean = 0.33 → 60 × 0.33 = 20
Frame 4 (uniq): [0, 1, 0, 1] → mean = 0.5 → 60 × 0.5 = 30
```

The sum-based approach is **conservative and non-oscillating**: it only reports FPS based on actually observed unique frames within the 1-second window. It doesn't extrapolate from incomplete data.

### Window Size

The ring buffer size is set to **~1 second of frames**:

```python
window_size = round(container_fps)  # 60fps video → 60-frame window
```

This means:
- 60fps container → 60-frame window (1.0 second)
- 30fps container → 30-frame window (1.0 second)
- 59.94fps container → 60-frame window (~1.0 second)

### Example: 30fps Content in 60fps Container

```
Frame 2:   sum = 1   → FPS = 1
Frame 4:   sum = 2   → FPS = 2
Frame 6:   sum = 3   → FPS = 3
...
Frame 58:  sum = 29  → FPS = 29
Frame 60:  sum = 30  → FPS = 30 ✓ (window full, stable)
Frame 62:  sum = 30  → FPS = 30 ✓ (remains stable)
```

### Ramp-Up Period

The FPS estimate ramps up gradually over the first second as the buffer fills with observed data:

- **During ramp-up**: FPS increases monotonically from 0 to true FPS
- **After ramp-up**: FPS is stable (for consistent content)

This is scientifically honest: we don't claim high FPS until we've actually observed enough unique frames to justify it.

### Trade-offs

| Window Size | Responsiveness | Stability |
|-------------|----------------|-----------|
| Smaller     | Fast (reacts quickly to FPS changes) | Noisy |
| Larger      | Slow (smooths out variations) | Stable |

The 1-second default balances responsiveness with stability for typical use cases.

## Core Concepts

### Frame Types

**FrameView** - Read-only reference to frame data:
```python
@dataclass(frozen=True, slots=True)
class FrameView:
    _data: np.ndarray  # (H, W, 3) uint8 RGB
    index: int         # 0-based frame index
    pts: int           # Presentation timestamp
```

**FramePair** - Two consecutive frames with release callback:
```python
@dataclass(frozen=True, slots=True)
class FramePair:
    prev: FrameView
    curr: FrameView
    _on_release: ReleaseCallback

    def release(self) -> None:
        """Signal source that buffers can be recycled."""
```

### FrameMetrics Monoid

Composable partial results from multiple analyzers:

```python
@dataclass(frozen=True, slots=True)
class FrameMetrics:
    frame_index: int
    is_duplicate: bool | None = None
    diff_ratio: float | None = None
    tear_rows: tuple[int, ...] | None = None
```

Multiple analyzers produce partials that get combined via `+`:
```python
dup_result + tear_result  # Merges non-None fields
```

### Compositor

Synchronization point that combines video frames and metrics:

```python
class Compositor(ABC):
    def process(
        self,
        pairs: list[FramePair],
        results: list[FrameMetrics],
    ) -> CompositorOutput:
        """Combine frames and metrics into composited output."""
```

**CompositorOutput** contains:
- `frame: np.ndarray` - Composited frame (owned buffer, reused)
- `metrics: AggregatedMetrics` - Windowed FPS, running averages, etc.

**VideoMetrics** - Per-video temporal aggregation:
```python
@dataclass(frozen=True, slots=True)
class VideoMetrics:
    video_index: int
    windowed_fps: float      # Last N frames (O(1) via RingBuffer)
    average_fps: float       # Since start
    total_frames_processed: int
    total_duplicates: int
    total_unique: int
    current_is_duplicate: bool
    current_diff_ratio: float
```

### Streaming Exporters

Write incrementally as frames are processed:

```python
class StreamingExporter(ABC):
    def open(self) -> None: ...
    def write_frame(self, output: CompositorOutput) -> None: ...
    def close(self) -> None: ...
```

Implementations:
- `StreamingCSVExporter` - Appends rows per frame, flushes for crash resilience
- `StreamingVideoExporter` - Encodes composited frames via PyAV

## Buffer Lifecycle

```
Source          Engine              Compositor       Exporter
  │                │                    │               │
  │  FramePair     │                    │               │
  │───────────────►│                    │               │
  │                │                    │               │
  │                │  pairs + results   │               │
  │                │───────────────────►│               │
  │                │                    │               │
  │                │  CompositorOutput  │               │
  │                │◄───────────────────│               │
  │                │                    │               │
  │  release()     │                    │               │
  │◄───────────────│                    │               │
  │                │                    │               │
  │  (can recycle) │      output        │               │
  │                │───────────────────────────────────►│
  │                │                    │               │
```

**Key points:**
- Source owns frame buffers (double-buffered)
- Compositor owns output buffer (single, reused)
- `release()` signals source after compositor copies data
- Export must complete before next `process()` (protects compositor buffer)
- Engine is O(1) in memory - no copies except compositor output

## Utilities

### RingBuffer

O(1) fixed-size circular buffer for windowed statistics:

```python
buf = RingBuffer(size=60, dtype=np.float32)
buf.push(1.0)  # O(1) - maintains running sum
buf.mean()     # O(1) - sum / count
```

Used by compositor for windowed FPS calculation without O(N) history storage.

## Usage Example

```python
from trdrop.video.reader import PyAVReader
from trdrop.source.sequential import SequentialFrameSource
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.compositor import SimpleCompositor
from trdrop.engine import StreamingEngine
from trdrop.export import StreamingCSVExporter, StreamingVideoExporter

# Setup sources
reader = PyAVReader("video.mp4")
source = SequentialFrameSource(reader)

# Setup compositor
compositor = SimpleCompositor(
    video_count=1,
    video_fps=[reader.fps],
    output_width=1920,
    output_height=1080,
)

# Setup exporters
csv_exporter = StreamingCSVExporter("metrics.csv")
video_exporter = StreamingVideoExporter("output.mp4", fps=reader.fps)

# Run streaming pipeline
engine = StreamingEngine(
    sources=[source],
    analyzers=[DuplicateDetector()],
    compositor=compositor,
    exporters=[csv_exporter, video_exporter],
)
engine.run()
```

## Overlay System

The compositor supports optional overlay elements rendered via QPainter onto a QImage backing store.

### FPSText

Simple text overlay showing current FPS:

```python
from trdrop.compositor.overlay.text import FPSText, TextStyle

text_style = TextStyle(
    color=QColor(255, 255, 255),
    shadow_color=QColor(0, 0, 0),
    font=QFont("Helvetica Neue", 24),
    shadow_offset=3,
)
fps_text = FPSText(text_style, prefix="FPS:")
```

### FrameratePlot

Real-time framerate graph with configurable features:

```python
from trdrop.compositor.overlay.plot import FrameratePlot, PlotStyle

plot_style = PlotStyle(
    line_color=QColor(255, 100, 200),
    background_color=QColor(0, 0, 0, 120),
    axis_color=QColor(236, 236, 236),
    grid_color=QColor(255, 255, 255, 60),
    text_color=QColor(255, 255, 255),
    shadow_color=QColor(0, 0, 0),
    font=plot_font,
    title_font=title_font,
    line_width=2,
    shadow_offset=2,
    show_grid=True,
    show_labels=True,
)

framerate_plot = FrameratePlot(
    plot_style,
    max_fps=60.0,           # Base Y-axis scale
    auto_scale=True,        # Dynamically adjust Y-axis
    show_smoothed=True,     # Fading smoothed trail
    time_anchor=1.0,        # Current time at right edge
)
```

**Features:**
- **Auto-scaling Y-axis**: Adjusts to data, uses recent 10% for fast adaptation
- **K suffix for large values**: 1000 → "1K", 1500 → "1.5K"
- **Nice axis labels**: Divisible by 4 (60, 120, 300, 1000, etc.)
- **Fading smoothed trail**: Moving average that fades toward current time
- **Configurable time anchor**: 0.0=left, 0.5=center, 1.0=right (default)

## Profiling

Enable performance profiling via environment variable to analyze pipeline bottlenecks.

### Usage

```bash
# Output to default ./trdrop_profile.csv
TRDROP_PROFILE=1 python your_script.py

# Output to custom path
TRDROP_PROFILE=/path/to/profile.csv python your_script.py
```

### Output Files

1. **`<path>.csv`** - Per-frame timing data
2. **`<path>.summary.txt`** - Aggregated statistics

### Tracked Stages

| Stage | Description |
|-------|-------------|
| `read_decode_ms` | PyAV frame decode time |
| `read_total_ms` | Total frame pair acquisition |
| `analysis_duplicate_ms` | Duplicate detection time |
| `analysis_total_ms` | All analyzers combined |
| `compositor_compose_ms` | Frame scaling/composition |
| `compositor_overlay_ms` | Overlay rendering |
| `compositor_total_ms` | Total compositor time |
| `overlay_fps_text_ms` | FPS text rendering |
| `overlay_plot_*_ms` | Plot components (background, grid, axes, line, trail, labels, title) |
| `export_video_convert_ms` | numpy → VideoFrame conversion |
| `export_video_encode_ms` | Video encoding |
| `export_video_total_ms` | Total video export |
| `export_csv_ms` | CSV write time |
| `frame_total_ms` | End-to-end frame time |

### Summary Output

```
TRDrop Profiling Summary
======================================================================

Total frames: 299
Total time: 7.89s
Average FPS: 37.9

Per-Stage Timing (ms/frame): mean ± std [min, max]
----------------------------------------------------------------------
  Read (decode)               1.064 ±  0.210  [  0.776,    3.386]
  Analysis (dup)              6.939 ±  0.832  [  5.162,   10.034]
  Compositor (compose)       13.692 ±  4.256  [  7.571,   20.048]
  Compositor (overlay)        1.219 ±  4.518  [  0.623,   78.909]
  ...

Compositor Overlay Breakdown (ms/frame): mean ± std
----------------------------------------------------------------------
  FPS Text                    0.301 ±  3.980
  Plot Line (exact)           0.438 ±  0.294
  Plot Trail (smoothed)       0.290 ±  0.182
  ...

Time Distribution (% of measured time):
----------------------------------------------------------------------
  Read             4.2%  ██
  Analysis        26.8%  █████████████
  Compositor      57.1%  ████████████████████████████
  Export Video    11.8%  █████

Pipeline Overlap Analysis:
----------------------------------------------------------------------
  Theoretical sequential time: 7,816.5 ms
  Actual wall clock time:      7,891.7 ms
  Time saved by parallelism:   -75.2 ms (-1.0%)
```

### Programmatic Access

```python
from trdrop.profiling import get_profiler

profiler = get_profiler()
if profiler.enabled:
    # Custom timing
    with profiler.time("custom_stage"):
        do_work()

    # Or manual
    profiler.add_timing("custom_stage", duration_ms)
```

## Future Extensions

- **PrefetchingFrameSource**: Background prefetch with ring buffer
- **TearDetector**: Analyzer for screen tearing artifacts
- **GPU acceleration**: OpenGL/Metal for overlay rendering and frame scaling
- **GUI integration**: Shared state for random seeking during/after processing
