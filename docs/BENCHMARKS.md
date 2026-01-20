# TRDrop v2 Performance Benchmarks

This document tracks performance measurements across versions to guide optimization efforts.

## How to Run Benchmarks

```bash
# Run the demo test with profiling enabled
TRDROP_PROFILE=examples/demo_profile.csv make test

# Or run specific benchmark
TRDROP_PROFILE=benchmark.csv uv run pytest tests/test_demo_overlay.py -v

# Run standardized benchmarks (1-4 videos)
TRDROP_PROFILE=benchmark.csv uv run pytest tests/benchmarks/ -v -s

# Run scaling analysis
TRDROP_PROFILE=benchmark.csv uv run pytest tests/benchmarks/test_benchmark.py::TestBenchmarkComparison::test_scaling_analysis -v -s
```

The profiler outputs:
- `<name>.csv` - Per-frame timing data
- `<name>.summary.txt` - Aggregated statistics

---

## Benchmark Configuration

**Test video:** 5 seconds, 60fps container, 30fps content (1280x720)
- Total frames: 300 (299 pairs analyzed)
- Pattern: NUMBER (frame counter overlay)

**Output:** 1280x720 with overlays (FPS text + framerate plot)

**Hardware:** _(fill in your hardware)_

---

## Benchmark Log

### 2025-01-19 - Initial v2 Engine (Baseline)

**Commit:** _(to be filled after commit)_

**Configuration:**
- `synchronous=True` (no async export)
- SimpleCompositor with FPSText + FrameratePlot
- DuplicateDetector analyzer

**Results:**

| Metric | Value |
|--------|-------|
| Total time | 7.89s |
| Average FPS | 37.9 |
| Frame time | 26.3 ± 6.4 ms |

**Per-Stage Breakdown:**

| Stage | Mean (ms) | Std (ms) | % of Total |
|-------|-----------|----------|------------|
| Read (decode) | 1.06 | 0.21 | 4.2% |
| Read (total) | 1.10 | 0.22 | - |
| Analysis (duplicate) | 6.94 | 0.83 | 26.8% |
| Compositor (compose) | 13.69 | 4.26 | - |
| Compositor (overlay) | 1.22 | 4.52 | - |
| Compositor (total) | 14.93 | 5.95 | 57.1% |
| Export Video | 3.08 | 1.43 | 11.8% |
| Export CSV | 0.03 | 0.01 | 0.1% |

**Compositor Overlay Breakdown:**

| Component | Mean (ms) | Std (ms) |
|-----------|-----------|----------|
| FPS Text | 0.30 | 3.98 |
| Plot Background | 0.06 | 0.01 |
| Plot Grid | 0.23 | 0.02 |
| Plot Axes | 0.02 | 0.00 |
| Plot Line | 0.44 | 0.29 |
| Plot Labels | 0.07 | 0.03 |
| Plot Title | 0.03 | 0.01 |
| **Overlay Total** | **1.15** | - |

**Pipeline Overlap:**
- Theoretical sequential: 7,816.5 ms
- Actual wall clock: 7,891.7 ms
- Overlap achieved: -1.0% (sync mode, no parallelism)

**Key Observations:**

1. **Compositor is the bottleneck (57.1%)** - specifically `compositor_compose` (frame scaling)
   - `_blit_scaled()` uses numpy fancy indexing for nearest-neighbor resize
   - Takes ~14ms per frame for 1280x720 → 1280x720 (no scaling needed!)

2. **Analysis is second (26.8%)** - duplicate detection
   - Grayscale conversion + pixel comparison at ~7ms
   - Could benefit from SIMD or GPU acceleration

3. **Export is efficient (11.8%)** - PyAV encoding
   - ~3ms total for H.264 encoding at CRF 18

4. **Overlay rendering is fast (1.45ms)** but has high variance
   - First frame spike (FPS text font caching?)
   - Plot line + trail: ~0.73ms combined

**Optimization Priorities:**

1. **compositor_compose** - Replace numpy fancy indexing with:
   - OpenCV `cv2.resize()`
   - PIL/Pillow resize
   - Skip entirely if no scaling needed (1:1 copy)

2. **analysis_duplicate** - Consider:
   - Chunk parallelization (already supported)
   - NumPy vectorization improvements
   - Downsampled comparison (compare every Nth pixel)

3. **Enable async export** - Run export in parallel with next frame's read+analysis

---

### 2025-01-19 - Multi-Video Scaling Analysis

**Test configuration:**
- Resolution: 1280x720 per video
- Duration: 2s @ 60fps container / 30fps content
- Layout: Horizontal (equal width per video)
- Overlays: FPS text + FrameratePlot per video

**Scaling Results:**

| Videos | FPS | Frame Time (ms) | Compositor (ms) | Slowdown |
|--------|-----|-----------------|-----------------|----------|
| 1 | 36.1 | 27.7 | 16.9 | 1.00x |
| 2 | 30.4 | 32.9 | 18.9 | 1.19x |
| 3 | 27.7 | 36.0 | 19.0 | 1.30x |
| 4 | 24.8 | 40.3 | 20.0 | 1.45x |

**Key Observations:**

1. **Sub-linear scaling achieved** - 4 videos only causes 1.45x slowdown (not 4x)
   - Read scales linearly (4.68ms for 4 videos vs 1.25ms for 1)
   - Analysis scales sub-linearly (9.4ms for 4 vs 7.1ms for 1)
   - Compositor scales very well (20ms for 4 vs 16.9ms for 1)

2. **Horizontal layout works correctly**
   - Each video gets `output_width / video_count` pixels
   - Remainder pixels added to last video
   - Each video scaled independently to fit its slot

3. **Per-video overlays render independently**
   - FPS text positioned at 5% from left edge of each video slot
   - Framerate plot positioned at bottom of each video slot

**Why scaling is sub-linear:**

The compositor `_blit_scaled()` operates on each video independently. With 4 videos, each gets 1/4 the output width:
- 1 video: 1280px wide slot → scale 1280→1280 (1:1)
- 4 videos: 320px wide slot each → scale 1280→320 (4:1 downsample)

Downsampling is faster than 1:1 copy because fewer pixels are written.

---

### 2025-01-19 - CROP Mode Optimization

**Commit:** CROP mode as default, removed smoothed trail

**Key Change:** Replaced scaling-based compositor with center-crop strategy.

The previous implementation used `_blit_scaled()` with numpy fancy indexing for all frames,
even when source and destination had the same resolution. The new CROP mode uses simple
numpy slice assignment - no index arrays, no scaling computation.

**Single Video Results (5s @ 60fps, 1280x720):**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total time | 7.89s | 3.80s | **2.1x faster** |
| Average FPS | 37.9 | 78.7 | **2.1x faster** |
| Frame time | 26.3ms | 12.6ms | **2.1x faster** |

**Per-Stage Breakdown:**

| Stage | Before (ms) | After (ms) | Improvement |
|-------|-------------|------------|-------------|
| Read (total) | 1.10 | 1.18 | ~same |
| Analysis (total) | 6.94 | 7.26 | ~same |
| Compositor (compose) | 13.69 | **0.07** | **196x faster** |
| Compositor (overlay) | 1.22 | 1.00 | 1.2x faster |
| Compositor (total) | 14.93 | **1.09** | **13.7x faster** |
| Export Video | 3.08 | 2.98 | ~same |

**Time Distribution Shift:**

| Stage | Before | After |
|-------|--------|-------|
| Read | 4.2% | 9.4% |
| Analysis | 26.8% | **57.9%** |
| Compositor | **57.1%** | 8.7% |
| Export | 11.8% | 23.7% |

**New Bottleneck:** Analysis (duplicate detection) is now the limiting factor at 57.9% of frame time.

**Multi-Video Scaling (CROP mode):**

| Videos | FPS | Frame Time (ms) | Compositor (ms) | Slowdown |
|--------|-----|-----------------|-----------------|----------|
| 1 | 77.6 | 12.9 | 1.56 | 1.00x |
| 2 | 65.7 | 15.2 | 1.48 | 1.18x |
| 3 | 54.5 | 18.3 | 1.79 | 1.42x |
| 4 | 42.1 | 23.7 | 2.03 | 1.84x |

**Per-Stage Speedup (Single Video):**

| Stage | Before (ms) | After (ms) | Speedup |
|-------|-------------|------------|---------|
| Read (total) | 1.10 | 1.18 | 0.93x (no change) |
| Analysis (total) | 6.94 | 7.26 | 0.96x (no change) |
| Compositor (compose) | 13.69 | 0.07 | 195.6x |
| Compositor (overlay) | 1.22 | 1.00 | 1.22x |
| Compositor (total) | 14.93 | 1.09 | 13.7x |
| Export Video | 3.08 | 2.98 | 1.03x (no change) |
| **Frame Total** | **26.3** | **12.6** | **2.09x** |

**Multi-Video Speedup (CROP vs Scaling):**

| Videos | Before (FPS) | After (FPS) | Speedup |
|--------|--------------|-------------|---------|
| 1 | 36.1 | 77.6 | 2.15x |
| 2 | 30.4 | 65.7 | 2.16x |
| 3 | 27.7 | 54.5 | 1.97x |
| 4 | 24.8 | 42.1 | 1.70x |

**Pipeline Overlap Analysis:**

Before (scaling mode):
- Theoretical sequential: 7,816.5 ms
- Actual wall clock: 7,891.7 ms
- Overlap: -1.0% (sync mode, no parallelism)

After (CROP mode):
- Theoretical sequential: 3,749.1 ms
- Actual wall clock: 3,799.6 ms
- Overlap: -1.3% (sync mode, no parallelism)

Pipeline overhead is ~50ms in both cases (initialization, teardown).
No inter-stage parallelism in synchronous mode.

**Scale Modes Available:**

| Mode | Description | Compose Time |
|------|-------------|--------------|
| CROP (default) | Center-crop, no scaling | 0.07ms |
| FIT | Scale to fit, letterbox | ~14ms (uses fancy indexing) |
| STRETCH | Scale to fill, ignores aspect | ~14ms (uses fancy indexing) |

---

### 2025-01-20 - Async Export Comparison

**Test:** 1 video at 1280x720, 3s duration (179 frames).

| Mode | Total Time | FPS | Frame Time |
|------|------------|-----|------------|
| Sync | 2.23s | 80.4 | 12.44ms |
| Async | 1.96s | 91.3 | 10.95ms |

**Speedup:** 1.136x (async vs sync)

**Per-frame timing:**

| Metric | Value |
|--------|-------|
| Time saved per frame | 1.49ms |
| Export time (sync) | 2.30ms |
| Read+Analysis time | 8.69ms |
| Max overlap potential | 2.30ms |
| Actual overlap achieved | 1.49ms (65% of potential) |

The async mode overlaps export with the next frame's read+analysis.
Not all export time is hidden because export (2.30ms) is shorter than
read+analysis (8.69ms), so the next frame's compositor must wait.

---

### 2025-01-20 - Memory Usage (Preliminary)

**Test:** 4 videos at 1280x720, 52 frames.

| Metric | Value |
|--------|-------|
| Memory after warmup (2 frames) | 10.6 MB |
| Memory after 50 frames | 10.7 MB |
| Memory growth | +0.07 MB |

**Note:** This is a short test. O(1) memory is the design goal - longer running
tests are needed to verify no slow leaks. The architecture uses double-buffering
with buffer reuse, which should provide constant memory usage.

---

## Notes

- All measurements on macOS with Python 3.12
- Using PyAV for video I/O
- QPainter for overlay rendering
- Run benchmarks after a warmup (first frame has initialization overhead)
