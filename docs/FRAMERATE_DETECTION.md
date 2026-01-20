# Framerate Detection: Theoretical Limitations

## The Quantization Problem

When detecting content framerate F within a container at rate C:

- We can only observe at container granularity (1/C seconds)
- Each content frame appears for `C/F` container frames on average
- If `C/F` is not an integer, we observe oscillation

### Examples with 60fps Container

| Content FPS | C/F Ratio | Duplicates per unique | Observed behavior |
|-------------|-----------|----------------------|-------------------|
| 60 | 1.0 | 0 | Exact: always 60fps |
| 30 | 2.0 | 1 | Exact: always 30fps |
| 20 | 3.0 | 2 | Exact: always 20fps |
| 24 | 2.5 | 1 or 2 | Oscillates: 30/20fps |
| 29.97 | 2.002 | mostly 1, rare 2 | Mostly 30, occasional 20 |
| 25 | 2.4 | 1 or 2 | Pattern: 30,30,20,30,30... |

### The 24fps Problem

With 60fps container and 24fps content:
- Ratio = 60/24 = 2.5
- Pattern over 5 content frames (in container frames):
  ```
  Content:    [A] [B] [C] [D] [E]
  Container:  A A B B B C C D D D E E ...
  Duplicates:  1   2   1   2   1
  Measured:   30  20  30  20  30 fps
  ```
- Windowed average converges to 24fps over time

### The 29.97fps Problem (NTSC)

With 60fps container and 29.97fps content:
- Ratio = 60/29.97 ≈ 2.002002
- Every ~500 frames, one extra duplicate appears
- Instantaneous measurement: 30fps or 20fps
- Needs long-term averaging to get 29.97fps

## Solution: Exponential Moving Average (EMA)

For display purposes, we smooth the measured values:

```python
smoothed = α * current + (1 - α) * previous_smoothed
```

Where:
- `α` close to 0: heavy smoothing, slow response
- `α` close to 1: light smoothing, fast response

Recommended values:
- `α = 0.1`: Good for stable display, ~10 frame response time
- `α = 0.05`: Very smooth, ~20 frame response time

### EMA for Frametime

Frametime (ms) = 1000 / FPS

When FPS oscillates between 20 and 30:
- Frametime oscillates between 50ms and 33.3ms
- EMA smooths to ~41.7ms (matches 24fps)

## Minimum Container Rate for Detection

To reliably detect content rate F, the container rate C should satisfy:

1. **Nyquist-like rule**: C ≥ 2F (at minimum)
2. **For exact detection**: C should be integer multiple of F
3. **For smooth averaging**: Window size ≥ C / gcd(C, F)

### Practical Guidelines

| Content FPS | Minimum Container | Recommended Container |
|-------------|-------------------|----------------------|
| 24 | 48 | 120 (5x) or 144 (6x) |
| 25 | 50 | 100 (4x) or 150 (6x) |
| 30 | 60 | 60 (2x) or 120 (4x) |
| 60 | 120 | 120 (2x) or 240 (4x) |

Higher container rates give more precise instantaneous measurements.

## Implementation Notes

1. **Raw values**: Store exact windowed FPS (sum of unique frames in window)
2. **Display values**: Apply EMA for smooth display
3. **Frametime**: Calculate from smoothed FPS, not raw
4. **History plots**: Can show raw values (jagged) or smoothed (clean)
