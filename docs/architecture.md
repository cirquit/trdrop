# TRDrop v2 Architecture

## Overview

TRDrop analyzes video files to detect the actual content framerate by identifying duplicate frames. A video recorded at 30fps but encoded in a 60fps container will have every other frame duplicated - TRDrop detects this pattern.

## Module Structure

```
src/trdrop/
├── types/              # Immutable data types
│   ├── frames.py       # FrameView, FramePair
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
├── engine/             # Orchestration
│   └── trdrop.py       # TrdropEngine, VideoResult
│
└── export/             # Result export (stubs)
    ├── csv.py
    └── json.py
```

## Core Concepts

### Frame Types

**FrameView** - Read-only reference to frame data with metadata:
```python
@dataclass(frozen=True, slots=True)
class FrameView:
    _data: np.ndarray  # (H, W, 3) uint8 RGB
    index: int         # 0-based frame index
    pts: int           # Presentation timestamp
```

**FramePair** - Two consecutive frames for comparison:
```python
@dataclass(frozen=True, slots=True)
class FramePair:
    prev: FrameView
    curr: FrameView
```

### FrameMetrics Monoid

`FrameMetrics` uses the monoid pattern for composable partial results:

```python
@dataclass(frozen=True, slots=True)
class FrameMetrics:
    frame_index: int
    is_duplicate: bool | None = None
    diff_ratio: float | None = None
    tear_rows: tuple[int, ...] | None = None
```

**Monoid properties:**
- Identity: `FrameMetrics.empty(idx)` - all fields None
- Combine: `metrics_a + metrics_b` - merges non-None fields
- Conflict detection: raises if both have different non-None values for same field

This allows multiple analyzers to produce partial results that get combined:
```python
dup_result = FrameMetrics(frame_index=5, is_duplicate=True, diff_ratio=0.001)
tear_result = FrameMetrics(frame_index=5, tear_rows=(120, 240))
combined = dup_result + tear_result  # Has all fields
```

### Interfaces

**VideoReader** (ABC) - Low-level video decoding:
```python
class VideoReader(ABC):
    def read(self, out: np.ndarray) -> bool  # Read into pre-allocated buffer
    def seek(self, frame_index: int) -> None
    def close(self) -> None
```

**FrameSource** (ABC) - Iterates frame pairs with double-buffering:
```python
class FrameSource(ABC):
    def __iter__(self) -> Iterator[FramePair]
    def close(self) -> None
```

**Mappable[In, Out]** (ABC) - Pure transformation:
```python
class Mappable(ABC, Generic[In, Out]):
    def map(self, input: In) -> Out
```

## Engine Architecture

### TrdropEngine

The engine orchestrates analysis with two-level parallelism:

```
┌─────────────────────────────────────────────────────────────┐
│                      TrdropEngine                           │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Video Worker Pool                      │    │
│  │  (processes multiple videos in parallel)            │    │
│  │                                                     │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐              │    │
│  │  │ Video 1 │  │ Video 2 │  │ Video 3 │  ...         │    │
│  │  └────┬────┘  └────┬────┘  └────┬────┘              │    │
│  │       │            │            │                   │    │
│  └───────┼────────────┼────────────┼───────────────────┘    │
│          │            │            │                        │
│          ▼            ▼            ▼                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Per-Video Processing (sequential frames)    │    │
│  │                                                     │    │
│  │  for each FramePair:                                │    │
│  │    ┌─────────────────────────────────────────┐      │    │
│  │    │        Analyzer Worker Pool             │      │    │
│  │    │  (runs analyzers in parallel per frame) │      │    │
│  │    │                                         │      │    │
│  │    │  ┌──────────┐  ┌──────────┐             │      │    │
│  │    │  │ Analyzer │  │ Analyzer │  ...        │      │    │
│  │    │  │    1     │  │    2     │             │      │    │
│  │    │  └────┬─────┘  └────┬─────┘             │      │    │
│  │    │       │             │                   │      │    │
│  │    │       ▼             ▼                   │      │    │
│  │    │  FrameMetrics + FrameMetrics = Combined │      │    │
│  │    └─────────────────────────────────────────┘      │    │
│  │                         │                           │    │
│  │                         ▼                           │    │
│  │                  metrics.append(combined)           │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                │
│                            ▼                                │
│                      VideoResult                            │
└─────────────────────────────────────────────────────────────┘
```

### Parallelization Strategy

**Level 1: Video Parallelism**
- Multiple videos processed concurrently via `ThreadPoolExecutor`
- Each video gets its own copies of analyzers (via `copy.deepcopy`)
- Controlled by `video_workers` parameter

**Level 2: Analyzer Parallelism**
- Within each video, analyzers run in parallel per frame
- Results combined using monoid `+` operator (fold/reduce)
- Controlled by `analyzer_workers` parameter

**Thread Safety**
- Analyzers are deep-copied per video to avoid shared state
- Each analyzer owns its internal buffers (`AnalysisBuffers`)
- Frame data is read-only during analysis

### Data Flow

```
VideoReader                    FrameSource                   Engine
    │                              │                            │
    │  read(buffer) -> bool        │                            │
    │◄─────────────────────────────│                            │
    │                              │                            │
    │                              │  __iter__() -> FramePair   │
    │                              │◄───────────────────────────│
    │                              │                            │
    │                              │  (double-buffer swap)      │
    │                              │                            │
    │                              │         FramePair          │
    │                              │───────────────────────────►│
    │                              │                            │
    │                              │                    ┌───────┴───────┐
    │                              │                    │   Analyzers   │
    │                              │                    │   (parallel)  │
    │                              │                    └───────┬───────┘
    │                              │                            │
    │                              │                    FrameMetrics[]
    │                              │                            │
    │                              │                    reduce(+, partials)
    │                              │                            │
    │                              │                      VideoResult
```

### Double-Buffer Frame Iteration

`SequentialFrameSource` uses two buffers to avoid allocation per frame:

```python
def __iter__(self) -> Iterator[FramePair]:
    buf_a = np.empty(shape, dtype=np.uint8)
    buf_b = np.empty(shape, dtype=np.uint8)

    reader.read(buf_a)  # First frame
    prev_view = FrameView(_data=buf_a, index=0, pts=0)

    for i in range(1, total_frames):
        reader.read(buf_b)  # Read into second buffer
        curr_view = FrameView(_data=buf_b, index=i, pts=...)

        yield FramePair(prev=prev_view, curr=curr_view)

        # Swap buffers (no copy, just reference swap)
        buf_a, buf_b = buf_b, buf_a
        prev_view = curr_view
```

### Buffer Lifecycle and Ownership

The engine controls buffer lifecycle through explicit `release()` calls.

**Contract:**
1. Source yields `FramePair` with references to internal buffers
2. Source guarantees data validity until `release()` is called
3. Engine calls `pair.release()` when done with the pair
4. Source can then recycle those buffers (for prefetching, etc.)

**Release callback interface:**
```python
class ReleaseCallback(ABC):
    @abstractmethod
    def __call__(self) -> None:
        """Called when the frame pair is no longer needed."""

@dataclass(frozen=True, slots=True)
class FramePair:
    prev: FrameView
    curr: FrameView
    _on_release: ReleaseCallback = _NOOP_RELEASE

    def release(self) -> None:
        self._on_release()
```

**Engine usage:**
```python
for pair in source:
    metrics = analyze(pair)
    rendered = render(pair, metrics)  # Creates NEW composited buffer
    pair.release()                     # Source can now recycle buffers
    export(rendered)                   # Runs while source prefetches next
```

**Key insight:** The composited/rendered frame is the natural "handoff point".
After rendering creates its own buffer, source buffers can be recycled while
the I/O-bound export runs in parallel with the next frame's read.

**Memory model:**
- Engine is O(1) in memory - no copies, just references
- Source manages its own buffer pool (double-buffer, ring buffer, etc.)
- Only the final composited frame is copied (once, for output)

**Source implementations:**
| Source | Strategy | Release behavior |
|--------|----------|------------------|
| `SequentialFrameSource` | Double-buffer | Marks buffer available for reuse |
| `MockFrameSource` | Allocates per frame | No-op (testing convenience) |
| `RingBufferFrameSource` | N-slot ring buffer | Returns slot to pool (future) |

## Analysis Engine

### NumpyAnalyzer

Core analysis using NumPy operations:

```python
class NumpyAnalyzer:
    def compare(self, prev, curr) -> tuple[bool, float]:
        # 1. Convert to grayscale (reuse buffer)
        # 2. Compute absolute difference
        # 3. Threshold to binary
        # 4. Count differing pixels
        # 5. Return (is_duplicate, diff_ratio)

    def detect_tears(self, prev, curr) -> tuple[int, ...]:
        # Row-by-row analysis for screen tearing
```

### AnalysisBuffers

Pre-allocated buffers to avoid per-frame allocation:

```python
@dataclass(slots=True)
class AnalysisBuffers:
    gray_a: np.ndarray    # Grayscale previous
    gray_b: np.ndarray    # Grayscale current
    diff: np.ndarray      # Difference image
    row_means: np.ndarray # Per-row mean (for tear detection)
```

## VideoResult

Final result for a single video:

```python
@dataclass(frozen=True, slots=True)
class VideoResult:
    path: Path
    fps: float                      # Container FPS
    total_frames: int
    metrics: tuple[FrameMetrics, ...]

    # Computed properties:
    unique_frames: int              # Non-duplicate count + 1
    duplicate_frames: int           # Duplicate count
    duration_sec: float             # total_frames / fps
    detected_fps: float             # unique_frames / duration
```

## Usage Example

```python
from trdrop.video.reader import PyAVReader
from trdrop.source.sequential import SequentialFrameSource
from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.engine.trdrop import TrdropEngine

# Setup
reader = PyAVReader("video.mp4")
source = SequentialFrameSource(reader)
engine = TrdropEngine([DuplicateDetector()], video_workers=4)

# Run analysis
results = engine.run([(Path("video.mp4"), source)])

# Access results
result = results[0]
print(f"Container FPS: {result.fps}")
print(f"Detected FPS: {result.detected_fps:.1f}")
print(f"Duplicates: {result.duplicate_frames}/{result.total_frames}")
```

## Future Extensions

- **PrefetchingFrameSource**: Hide I/O latency with background prefetch
- **TearDetector**: Detect screen tearing artifacts
- **Renderers**: Overlay analysis results on video frames
- **Exporters**: CSV/JSON export of per-frame metrics
- **GUI Integration**: Real-time preview with Qt widgets
