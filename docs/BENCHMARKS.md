# TRDrop v2 Performance Benchmarks

This document tracks performance measurements across versions to guide optimization efforts.

## How to Run Benchmarks

```bash
# Run the demo test with profiling enabled
TRDROP_PROFILE=examples/demo_profile.csv make test

# Or run specific benchmark
TRDROP_PROFILE=benchmark.csv uv run pytest tests/test_demo_overlay.py -v
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
| Plot Line (exact) | 0.44 | 0.29 |
| Plot Trail (smoothed) | 0.29 | 0.18 |
| Plot Labels | 0.07 | 0.03 |
| Plot Title | 0.03 | 0.01 |
| **Overlay Total** | **1.45** | - |

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

## Performance Targets

| Metric | Current | Target | Notes |
|--------|---------|--------|-------|
| Frame time | 26.3ms | <16.7ms | Real-time for 60fps playback |
| Throughput | 37.9 fps | >60 fps | Faster than real-time |
| Memory | O(1) | O(1) | Already achieved |

---

## Notes

- All measurements on macOS with Python 3.12
- Using PyAV for video I/O
- QPainter for overlay rendering
- Run benchmarks after a warmup (first frame has initialization overhead)
