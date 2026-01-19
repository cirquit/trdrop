#!/usr/bin/env python3
"""
Example 5: Frame Difference Analysis (TRDrop Core Algorithm)

Demonstrates the frame comparison technique used for detecting real FPS.
This is the core algorithm that TRDrop uses to detect duplicate frames.
"""

import av
import numpy as np
from collections import deque
import sys


def analyze_frame_differences(video_path: str, pixel_threshold: int = 5,
                               max_frames: int = 300):
    """
    Analyze frame-to-frame differences to detect real framerate.

    Args:
        video_path: Path to video file
        pixel_threshold: Max difference (0-255) to consider pixels "same"
        max_frames: Maximum frames to analyze
    """
    print(f"Analyzing: {video_path}")
    print(f"Pixel threshold: {pixel_threshold}")
    print("="*60)

    with av.open(video_path) as container:
        stream = container.streams.video[0]
        recorded_fps = float(stream.average_rate) if stream.average_rate else 60.0

        print(f"Recorded FPS: {recorded_fps:.3f}")
        print(f"Resolution: {stream.width}x{stream.height}")
        print()

        # Circular buffer for rolling FPS calculation (sized to 1 second)
        window_size = int(recorded_fps)
        diff_buffer = deque([1.0] * window_size, maxlen=window_size)

        prev_gray = None
        results = []

        for frame_idx, frame in enumerate(container.decode(stream)):
            if frame_idx >= max_frames:
                break

            # Convert to grayscale for comparison
            gray_frame = frame.reformat(format="gray")
            gray = gray_frame.to_ndarray()

            if prev_gray is not None:
                # Compare frames
                diff = np.abs(gray.astype(np.int16) - prev_gray.astype(np.int16))

                # Count pixels that differ more than threshold
                different_pixels = np.sum(diff > pixel_threshold)
                total_pixels = diff.size
                diff_percentage = 100 * different_pixels / total_pixels

                # Is this a "new" frame? (using 0.1% threshold)
                is_different = diff_percentage > 0.1

                # Update buffer (1.0 = new frame, 0.0 = duplicate)
                diff_buffer.append(1.0 if is_different else 0.0)

                # Calculate current "real" FPS
                real_fps = sum(diff_buffer)

                results.append({
                    "frame": frame_idx,
                    "pts": frame.pts,
                    "time": frame.time,
                    "is_different": is_different,
                    "diff_percentage": diff_percentage,
                    "real_fps": real_fps,
                })

                # Print every second
                if frame_idx % int(recorded_fps) == 0:
                    print(f"Frame {frame_idx:4d} | Real FPS: {real_fps:5.1f} | "
                          f"Diff: {diff_percentage:5.2f}% | "
                          f"{'NEW' if is_different else 'DUP'}")

            prev_gray = gray.copy()

        return results, recorded_fps


def calculate_frametime(results: list, recorded_fps: float):
    """Calculate frametime based on consecutive duplicate detection."""
    print("\n" + "="*60)
    print("Frametime Analysis")
    print("="*60)

    frametimes = []
    consecutive_dups = 0

    for i, r in enumerate(results):
        if r["is_different"]:
            if consecutive_dups > 0:
                # Frametime = (duplicates + 1) / recorded_fps * 1000 ms
                frametime_ms = (consecutive_dups + 1) / recorded_fps * 1000
                frametimes.append(frametime_ms)

            consecutive_dups = 0
        else:
            consecutive_dups += 1

    if frametimes:
        avg_frametime = np.mean(frametimes)
        min_frametime = np.min(frametimes)
        max_frametime = np.max(frametimes)

        print(f"\nFrametime Statistics:")
        print(f"  Average: {avg_frametime:.2f} ms")
        print(f"  Min:     {min_frametime:.2f} ms")
        print(f"  Max:     {max_frametime:.2f} ms")
        print(f"  Samples: {len(frametimes)}")

        # Histogram of frametimes
        print(f"\nFrametime Distribution:")
        bins = [0, 8.3, 16.7, 33.3, 50, 100, 1000]  # 120, 60, 30, 20, 10 fps equivalents
        labels = ["<8.3ms (>120)", "8.3-16.7ms (60-120)", "16.7-33.3ms (30-60)",
                  "33.3-50ms (20-30)", "50-100ms (10-20)", ">100ms (<10)"]

        for i in range(len(bins) - 1):
            count = sum(1 for ft in frametimes if bins[i] <= ft < bins[i+1])
            if count > 0:
                print(f"  {labels[i]}: {count} ({100*count/len(frametimes):.1f}%)")

    return frametimes


def detect_tears(gray_a: np.ndarray, gray_b: np.ndarray,
                 pixel_threshold: int = 5, row_threshold: float = 0.1):
    """
    Detect screen tears by analyzing row-by-row differences.

    A tear is detected when rows transition from "same" to "different"
    (or vice versa) sharply.
    """
    height = gray_a.shape[0]
    diff = np.abs(gray_a.astype(np.int16) - gray_b.astype(np.int16))

    # Calculate difference percentage per row
    row_diffs = []
    for y in range(height):
        row = diff[y, :]
        diff_pixels = np.sum(row > pixel_threshold)
        row_diffs.append(diff_pixels / len(row))

    # Detect transitions (potential tears)
    tears = []
    for y in range(1, height):
        prev_diff = row_diffs[y - 1]
        curr_diff = row_diffs[y]

        # Sharp transition from similar to different
        if prev_diff < row_threshold and curr_diff >= row_threshold:
            tears.append({"row": y, "type": "start", "diff": curr_diff})
        # Sharp transition from different to similar
        elif prev_diff >= row_threshold and curr_diff < row_threshold:
            tears.append({"row": y, "type": "end", "diff": prev_diff})

    return tears, row_diffs


def analyze_tears(video_path: str, max_frames: int = 100):
    """Analyze video for screen tears."""
    print("\n" + "="*60)
    print("Tear Detection Analysis")
    print("="*60)

    with av.open(video_path) as container:
        stream = container.streams.video[0]
        prev_gray = None
        total_tears = 0

        for frame_idx, frame in enumerate(container.decode(stream)):
            if frame_idx >= max_frames:
                break

            gray = frame.reformat(format="gray").to_ndarray()

            if prev_gray is not None:
                tears, _ = detect_tears(prev_gray, gray)

                if tears:
                    total_tears += len(tears)
                    if frame_idx < 20:  # Only print first few
                        print(f"Frame {frame_idx}: {len(tears)} potential tear(s)")
                        for t in tears:
                            print(f"    Row {t['row']}: {t['type']} (diff: {t['diff']:.2f})")

            prev_gray = gray.copy()

        print(f"\nTotal potential tears detected: {total_tears}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python 05_frame_diff_analysis.py <video_path> [pixel_threshold] [max_frames]")
        print("\nExample: python 05_frame_diff_analysis.py gameplay.mp4 5 300")
        print("\nThis analyzes frame differences to detect:")
        print("  - Real FPS (vs recorded FPS)")
        print("  - Frametime variations")
        print("  - Screen tears")
        sys.exit(1)

    video_path = sys.argv[1]
    pixel_threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    max_frames = int(sys.argv[3]) if len(sys.argv) > 3 else 300

    try:
        # Main analysis
        results, recorded_fps = analyze_frame_differences(
            video_path,
            pixel_threshold=pixel_threshold,
            max_frames=max_frames
        )

        # Frametime analysis
        frametimes = calculate_frametime(results, recorded_fps)

        # Tear analysis
        analyze_tears(video_path, max_frames=min(100, max_frames))

        # Summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)

        if results:
            avg_real_fps = np.mean([r["real_fps"] for r in results])
            dup_frames = sum(1 for r in results if not r["is_different"])
            total = len(results)

            print(f"Recorded FPS:     {recorded_fps:.2f}")
            print(f"Average Real FPS: {avg_real_fps:.2f}")
            print(f"Duplicate Frames: {dup_frames}/{total} ({100*dup_frames/total:.1f}%)")

    except FileNotFoundError:
        print(f"Error: File not found: {video_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
