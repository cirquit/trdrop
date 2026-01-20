# TRDrop v2 Performance Benchmarks

## Run Benchmarks

```bash
make benchmark
```

Output shows:
- Per-stage timing for 1-4 video configurations
- Scaling analysis (slowdown relative to single video)
- Async vs sync export comparison with pipeline overlap
- Video encoder being used (auto-detected)

---

## Current Performance (v0.6)

**Config:** 1920x1080 output, 1280x720 sources, 2s @ 60fps
**Encoder:** h264_videotoolbox (HW) - auto-detected

### Multi-Video Scaling (sync mode)

| N | FPS | ms/fr | Read | Analyze | Compose | Overlay | VidExp |
|---|-----|-------|------|---------|---------|---------|--------|
| 1 | 98 | 10.2 | 1.39 | 0.18 | 0.15 | 1.16 | 4.54 |
| 2 | 110 | 9.1 | 1.65 | 0.30 | 0.60 | 1.47 | 4.21 |
| 3 | 89 | 11.3 | 2.13 | 0.44 | 0.73 | 2.25 | 4.84 |
| 4 | 86 | 11.7 | 2.15 | 0.58 | 0.84 | 2.56 | 4.65 |

**Scaling:** 1v=1.00x, 2v=0.89x, 3v=1.11x, 4v=1.14x

### Async Export (1 video, 3s)

| Mode | FPS | ms/frame | Speedup |
|------|-----|----------|---------|
| Sync | 119 | 8.40 | - |
| Async | 162 | 6.18 | 1.36x |

Pipeline overlap: read=100%, analysis=100%

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

**Per-video overlay cost:** ~1.2ms (FPS text + framerate + frametime plots)

### Plot Operation Breakdown

| Operation | Time (ms) | Notes |
|-----------|-----------|-------|
| Static cache blit | 0.02 | Background, grid, axes, labels (cached to QPixmap) |
| Line drawing (AA) | 0.45 | Main cost - QPainter anti-aliased path |
| Markers | 0.01 | Start marker, time indicator |

**Optimizations applied:**
- Static elements cached to QPixmap (background, grid, axes, labels)
- Shadow drawn without AA for speed
- Cache invalidated only on bounds/scale change

Line drawing with anti-aliasing remains the dominant cost (~40% of overlay time).
Software AA is inherently expensive; GPU-based rendering would eliminate this.

---

## Historical Reference

### v0.1 → v0.6 Progression

| Version | 1-video FPS | Bottleneck | Key Change |
|---------|-------------|------------|------------|
| v0.1 | 20 | Compose (32ms) | FIT scaling, QImage conversion |
| v0.2 | 59 | Compose (0.14ms) | CROP mode, direct slice assignment |
| v0.3 | 63 | Compose (0.14ms) | Zero-copy QImage buffer |
| v0.4 | 60 | Analysis (7.5ms) | Added frametime plot |
| v0.5 | 117 | Read (1.3ms) | Numba JIT + stride 4x4 analysis |
| v0.6 | **162** | Export (4.5ms) | Parallel reads, async export, HW encoding, static cache |

### Scale Mode Comparison

| Mode | Compose Time | Notes |
|------|--------------|-------|
| CROP | <1ms | Direct slice assignment, center-crop |
| FIT | 10-31ms | Numpy fancy indexing, preserves aspect |

CROP is default. Use FIT only when letterboxing is required.

---

## Video Encoding

### Hardware Encoder Auto-Detection

The video exporter automatically detects and uses the best available encoder:

| Platform | Hardware | Encoder | Speedup vs libx264 |
|----------|----------|---------|-------------------|
| macOS | Apple Silicon/Intel | h264_videotoolbox | ~20% |
| Windows/Linux | NVIDIA GPU | h264_nvenc | ~40% |
| Windows | AMD GPU | h264_amf | ~30% |
| Windows/Linux | Intel GPU | h264_qsv | ~25% |
| Any | CPU (fallback) | libx264 | baseline |

Detection priority: videotoolbox → nvenc → amf → qsv → vaapi → libx264

### Encoder Comparison (1920x1080)

| Encoder | Total | Convert | Encode | Type |
|---------|-------|---------|--------|------|
| libx264 medium | 6.4ms | 1.0ms | 5.4ms | SW |
| libx264 ultrafast | 5.6ms | 1.2ms | 4.4ms | SW |
| h264_videotoolbox | 4.3ms | 1.4ms | 3.0ms | HW |

Hardware encoding offloads work to dedicated silicon, freeing CPU for other stages.

---

## Notes

- Measurements on macOS, Python 3.12, Apple Silicon
- First 5 frames excluded from averages (JIT warmup)
- PyAV for video I/O, QPainter for overlays
- Encoder shown in benchmark output and profiler summary
