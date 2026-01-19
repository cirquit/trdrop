# PyAV Examples for TRDrop

Minimal examples demonstrating PyAV usage for video analysis.

## Setup

```bash
pip install av numpy
```

## Examples

### 01. Read Video Info

Extract metadata from a video file.

```bash
python 01_read_video_info.py sample.mp4
```

### 02. Iterate Frames

Iterate through frames and convert to numpy arrays.

```bash
python 02_iterate_frames.py sample.mp4 10
```

### 03. Seek Frames

Seek to specific times/frames in a video.

```bash
python 03_seek_frames.py sample.mp4 5.0
```

### 04. Write Video

Create video files from numpy arrays.

```bash
python 04_write_video.py ./output/
```

### 05. Frame Diff Analysis

**Core TRDrop algorithm** - Detect real FPS, frametime, and tears.

```bash
python 05_frame_diff_analysis.py gameplay.mp4 5 300
```

Arguments:
- `video_path`: Input video file
- `pixel_threshold` (default: 5): Max pixel difference (0-255) to consider "same"
- `max_frames` (default: 300): Maximum frames to analyze

## Key Concepts

### Frame Iteration Pattern

```python
import av

with av.open("video.mp4") as container:
    for frame in container.decode(video=0):
        array = frame.reformat(format="rgb24").to_ndarray()
        # Process array...
```

### Grayscale for Analysis

```python
gray = frame.reformat(format="gray").to_ndarray()
# Shape: (height, width), dtype: uint8
```

### Frame Comparison

```python
diff = np.abs(frame_a.astype(np.int16) - frame_b.astype(np.int16))
is_different = np.any(diff > threshold)
```

## Reference

See [docs/pyav-reference.md](../../docs/pyav-reference.md) for comprehensive API documentation.
