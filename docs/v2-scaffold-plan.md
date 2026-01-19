# TRDrop v2 - First Scaffold Commit

## Goal

Create first commit that establishes the new architecture skeleton. Remove outdated code, add new type stubs, update tests.

---

## What to KEEP

| Module | Notes |
|--------|-------|
| `video/reader.py` | `PyAVReader` is correct |
| `core/analyzer.py` | `NumpyAnalyzer`, `AnalysisBuffers`, chunk functions |
| `gui/app.py` | Basic Qt setup |
| `gui/widgets/*` | Viewport and FPSPlot widgets |
| `tests/testkit/*` | Test infrastructure |

## What to REMOVE

| File | Reason |
|------|--------|
| `core/types.py` | Old `FrameResult`, `VideoAnalysis` - replaced by pipeline types |
| `session/manager.py` | Old `SessionManager`, `Session` - replaced by pipeline |
| `tests/test_core.py` lines 201-308 | `TestFrameResult`, `TestVideoAnalysis` tests for removed types |

## What to STUB (new modules)

| File | Contents |
|------|----------|
| `pipeline/types.py` | `DuplicateResult`, `TearResult`, `VideoFrameState`, `CompositeFrameState` |
| `pipeline/storage.py` | `FrameResultSlot`, `VideoResultBuffer` |
| `pipeline/analyzers.py` | `DuplicateAnalyzer`, `TearAnalyzer` wrapping `NumpyAnalyzer` |
| `pipeline/renderers.py` | `Renderer` protocol stub |
| `pipeline/exporters.py` | `Exporter` protocol stub |
| `pipeline/pipeline.py` | `ProcessingPipeline` stub |
| `preview/system.py` | `PreviewSystem` stub |

## What to ADAPT

| File | Changes |
|------|---------|
| `gui/main_window.py` | Remove `SessionManager` usage, add TODO comments |
| `export/csv.py` | Disable temporarily (old types removed) |
| `export/json.py` | Disable temporarily (old types removed) |
| `core/__init__.py` | Update exports |
| `session/__init__.py` | Keep only `LayoutMode` enum |

---

## New Directory Structure

```
src/trdrop/
├── core/
│   ├── __init__.py          # Export NumpyAnalyzer, AnalysisBuffers
│   └── analyzer.py          # KEEP unchanged
├── video/
│   └── reader.py            # KEEP unchanged
├── pipeline/                 # NEW
│   ├── __init__.py
│   ├── types.py             # Result types, frame states
│   ├── storage.py           # Pre-allocated buffers
│   ├── analyzers.py         # DuplicateAnalyzer, TearAnalyzer
│   ├── renderers.py         # Renderer protocol
│   ├── exporters.py         # Exporter protocol
│   └── pipeline.py          # ProcessingPipeline
├── preview/                  # NEW
│   ├── __init__.py
│   └── system.py            # PreviewSystem
├── session/
│   ├── __init__.py          # Export LayoutMode only
│   └── manager.py           # DELETE contents, keep LayoutMode
├── export/
│   ├── csv.py               # Stub (TODO: adapt to new types)
│   └── json.py              # Stub (TODO: adapt to new types)
└── gui/
    ├── main_window.py       # Remove SessionManager, add TODO
    └── widgets/             # KEEP unchanged
```

---

## Files to Create/Modify

### 1. `pipeline/types.py` (NEW)

```python
@dataclass(slots=True)
class DuplicateResult:
    diff_ratio: float
    is_duplicate: bool

@dataclass(slots=True)
class TearResult:
    tear_rows: tuple[int, ...]

@dataclass(slots=True)
class VideoFrameState:
    video_id: int
    frame_idx: int
    pts: int
    duplicate: DuplicateResult | None = None
    tear: TearResult | None = None

@dataclass(slots=True)
class CompositeFrameState:
    frame_idx: int
    videos: tuple[VideoFrameState, ...]
```

### 2. `pipeline/storage.py` (NEW)

```python
@dataclass(slots=True)
class FrameResultSlot:
    pts: int = 0
    has_duplicate: bool = False
    diff_ratio: float = 0.0
    is_duplicate: bool = False
    has_tear: bool = False
    tear_rows: tuple[int, ...] = ()

class VideoResultBuffer:
    def __init__(self, total_frames: int): ...
    @property
    def computed_up_to(self) -> int: ...
```

### 3. `pipeline/analyzers.py` (NEW)

```python
class DuplicateAnalyzer:
    """Wraps NumpyAnalyzer.compare() with owned buffers."""
    def analyze(self, prev: np.ndarray, curr: np.ndarray) -> DuplicateResult: ...

class TearAnalyzer:
    """Wraps NumpyAnalyzer.detect_tears() with owned buffers."""
    def analyze(self, prev: np.ndarray, curr: np.ndarray) -> TearResult: ...
```

### 4. `pipeline/pipeline.py` (NEW - stub)

```python
class ProcessingPipeline:
    def run(self) -> None:
        raise NotImplementedError
```

### 5. `preview/system.py` (NEW - stub)

```python
class PreviewSystem:
    def seek_to(self, frame_idx: int) -> CompositeFrameState | None:
        raise NotImplementedError
```

### 6. Remove old types from `core/types.py`

Delete entire file (FrameResult, VideoAnalysis).

### 7. Update `session/manager.py`

Keep only `LayoutMode` enum. Delete `Session`, `SessionManager`.

### 8. Update `gui/main_window.py`

Remove SessionManager imports and usage. Add TODO comments for pipeline integration.

### 9. Update `tests/test_core.py`

- Keep `TestNumpyAnalyzer` (lines 16-123)
- Keep `TestChunkFunctions` (lines 126-198)
- Remove `TestFrameResult` (lines 201-221)
- Remove `TestVideoAnalysis` (lines 224-308)
- Add `TestPipelineTypes` for new types

---

## Test Plan

```bash
uv run pytest tests/test_core.py -v
```

Expected:
- `TestNumpyAnalyzer`: 8 tests pass (analyzer unchanged)
- `TestChunkFunctions`: 4 tests pass (chunk functions unchanged)
- `TestPipelineTypes`: New tests for `DuplicateResult`, `TearResult`, `VideoFrameState`

---

## Commit Message

```
feat: scaffold new pipeline architecture

- Add pipeline/ module with types, storage, analyzers stubs
- Add preview/ module with PreviewSystem stub
- Remove old FrameResult, VideoAnalysis types
- Remove old SessionManager (keep LayoutMode)
- Update tests for new architecture

Breaking change: Old session-based API removed
```

---

## Verification

1. `uv run pytest tests/ -v` - all tests pass
2. `uv run python -c "from trdrop.pipeline import *"` - imports work
3. `uv run python -c "from trdrop.preview import *"` - imports work
