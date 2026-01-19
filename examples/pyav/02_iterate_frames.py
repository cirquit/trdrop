#!/usr/bin/env python3
"""
Example 2: Iterate Through Video Frames

Demonstrates frame-by-frame iteration and accessing frame data.
"""

import av
import numpy as np
import sys


def iterate_frames(video_path: str, max_frames: int = 10):
    """Iterate through video frames and print information."""
    with av.open(video_path) as container:
        stream = container.streams.video[0]

        print(f"Iterating through frames (max {max_frames})...")
        print(f"Stream: {stream.width}x{stream.height} @ {stream.average_rate} fps")
        print()

        for i, frame in enumerate(container.decode(stream)):
            if i >= max_frames:
                break

            # Frame properties
            print(f"Frame {i}:")
            print(f"  PTS:       {frame.pts}")
            print(f"  Time:      {frame.time:.4f}s" if frame.time else "  Time:      None")
            print(f"  Size:      {frame.width}x{frame.height}")
            print(f"  Format:    {frame.format.name}")
            print(f"  Pict Type: {frame.pict_type} ({'I' if frame.pict_type == 1 else 'P' if frame.pict_type == 2 else 'B' if frame.pict_type == 3 else '?'})")

            # Convert to numpy array
            rgb_frame = frame.reformat(format="rgb24")
            array = rgb_frame.to_ndarray()

            print(f"  NumPy:     shape={array.shape}, dtype={array.dtype}")
            print(f"  Mean RGB:  R={array[:,:,0].mean():.1f}, G={array[:,:,1].mean():.1f}, B={array[:,:,2].mean():.1f}")
            print()


def iterate_frames_grayscale(video_path: str, max_frames: int = 5):
    """Iterate and convert to grayscale (useful for analysis)."""
    print("\n" + "="*60)
    print("Grayscale iteration (for analysis):")
    print("="*60 + "\n")

    with av.open(video_path) as container:
        stream = container.streams.video[0]
        prev_gray = None

        for i, frame in enumerate(container.decode(stream)):
            if i >= max_frames:
                break

            # Convert directly to grayscale
            gray_frame = frame.reformat(format="gray")
            gray_array = gray_frame.to_ndarray()

            # Compare with previous frame
            if prev_gray is not None:
                diff = np.abs(gray_array.astype(np.int16) - prev_gray.astype(np.int16))
                mean_diff = diff.mean()
                max_diff = diff.max()
                changed_pixels = np.sum(diff > 5)  # Threshold of 5
                total_pixels = diff.size

                print(f"Frame {i}: mean_diff={mean_diff:.2f}, max_diff={max_diff}, "
                      f"changed={changed_pixels}/{total_pixels} ({100*changed_pixels/total_pixels:.1f}%)")
            else:
                print(f"Frame {i}: (first frame, no comparison)")

            prev_gray = gray_array.copy()


def main():
    if len(sys.argv) < 2:
        print("Usage: python 02_iterate_frames.py <video_path> [max_frames]")
        print("\nExample: python 02_iterate_frames.py sample.mp4 5")
        sys.exit(1)

    video_path = sys.argv[1]
    max_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    try:
        iterate_frames(video_path, max_frames)
        iterate_frames_grayscale(video_path, max_frames)

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
