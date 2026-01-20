# TRDrop v2 Performance Benchmarks

## Run Benchmarks

```bash
make benchmark
```

Output shows:
- Per-stage timing for 1-4 video configurations
- Scaling analysis (slowdown relative to single video)
- Async vs sync export comparison with pipeline overlap

---

## Current Performance (v0.5)

**Config:** 1920x1080 output, 1280x720 sources, 2s @ 60fps

### Multi-Video Scaling (sync mode)

| N | FPS | ms/fr | Read | Analyze | Compose | Overlay | VidExp |
|---|-----|-------|------|---------|---------|---------|--------|
| 1 | 112 | 8.9 | 1.45 | 0.17 | 0.13 | 1.22 | 4.87 |
| 2 | 94 | 10.6 | 2.72 | 0.34 | 0.59 | 1.61 | 4.88 |
| 3 | 75 | 13.4 | 3.87 | 0.49 | 0.75 | 2.46 | 5.38 |
| 4 | 63 | 15.9 | 5.43 | 0.64 | 0.85 | 3.13 | 5.37 |

**Scaling:** 1v=1.00x, 2v=1.19x, 3v=1.50x, 4v=1.78x

### Async Export (1 video, 3s)

| Mode | FPS | ms/frame | Speedup |
|------|-----|----------|---------|
| Sync | 114 | 8.78 | - |
| Async | 133 | 7.54 | 1.17x |

Pipeline overlap: read=100%, analysis=101%

---

## Analysis Strategies

Default: `numba_stride_4x4` (compares every 4th pixel in both dimensions with JIT)

| Strategy | Time (ms) | Speedup | Pixels |
|----------|-----------|---------|--------|
| full | 12.17 | 1.0x | 921,600 |
| stride_4x4 | 0.63 | 19x | 57,600 |
| numba_stride_4x4 | **0.15** | **83x** | 57,600 |

Falls back to `stride_4x4` if numba unavailable.

---

## Overlay Performance

**Per-video overlay cost:** ~3ms (FPS text + framerate + frametime plots)

### Plot Operation Breakdown

| Operation | Time (ms) | % |
|-----------|-----------|---|
| Line drawing | 1.37 | 80% |
| Grid | 0.17 | 10% |
| Labels | 0.06 | 3% |
| Background | 0.05 | 3% |
| Other | 0.05 | 4% |

Line drawing dominates. Potential optimization: QPainterPath caching, point downsampling.

---

## Historical Reference

### v0.1 → v0.5 Progression

| Version | 1-video FPS | Bottleneck | Key Change |
|---------|-------------|------------|------------|
| v0.1 | 20 | Compose (32ms) | FIT scaling, QImage conversion |
| v0.2 | 59 | Compose (0.14ms) | CROP mode, direct slice assignment |
| v0.3 | 63 | Compose (0.14ms) | Zero-copy QImage buffer |
| v0.4 | 60 | Analysis (7.5ms) | Added frametime plot |
| v0.5 | **117** | Read (1.3ms) | Numba JIT + stride 4x4 analysis |

### Scale Mode Comparison

| Mode | Compose Time | Notes |
|------|--------------|-------|
| CROP | <1ms | Direct slice assignment, center-crop |
| FIT | 10-31ms | Numpy fancy indexing, preserves aspect |

CROP is default. Use FIT only when letterboxing is required.

---

## Notes

- Measurements on macOS, Python 3.12, Apple Silicon
- First 5 frames excluded from averages (JIT warmup)
- PyAV for video I/O, QPainter for overlays
