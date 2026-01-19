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
│   └── types.py        # VideoMetrics, AggregatedMetrics, CompositorOutput
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

## Future Extensions

- **PrefetchingFrameSource**: Background prefetch with ring buffer
- **TearDetector**: Analyzer for screen tearing artifacts
- **Text overlays**: Font rendering in compositor
- **GUI integration**: Shared state for random seeking during/after processing
- **Profiling**: Per-stage timing and pipeline visualization
