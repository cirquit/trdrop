#!/usr/bin/env python3
"""
Example 4: Write Video Files

Demonstrates how to create video files from numpy arrays.
"""

import av
import numpy as np
from fractions import Fraction
import sys


def create_gradient_video(output_path: str, width: int = 640, height: int = 480,
                          fps: int = 30, duration_sec: float = 3.0):
    """Create a video with animated color gradient."""
    total_frames = int(fps * duration_sec)

    print(f"Creating gradient video: {output_path}")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"  Duration: {duration_sec}s ({total_frames} frames)")

    with av.open(output_path, mode="w") as container:
        # Add video stream
        stream = container.add_stream("libx264", rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = "yuv420p"

        # Optional: Set quality (lower crf = better quality)
        stream.options = {"crf": "23"}

        for frame_idx in range(total_frames):
            # Create gradient that changes over time
            t = frame_idx / total_frames

            # Generate RGB image
            img = np.zeros((height, width, 3), dtype=np.uint8)

            # Horizontal gradient with time-varying colors
            for x in range(width):
                r = int(255 * (0.5 + 0.5 * np.sin(2 * np.pi * (t + x / width))))
                g = int(255 * (0.5 + 0.5 * np.sin(2 * np.pi * (t + x / width + 1/3))))
                b = int(255 * (0.5 + 0.5 * np.sin(2 * np.pi * (t + x / width + 2/3))))
                img[:, x] = [r, g, b]

            # Convert numpy array to VideoFrame
            frame = av.VideoFrame.from_ndarray(img, format="rgb24")

            # Encode and mux
            for packet in stream.encode(frame):
                container.mux(packet)

            if (frame_idx + 1) % fps == 0:
                print(f"  Progress: {frame_idx + 1}/{total_frames} frames")

        # Flush encoder
        for packet in stream.encode():
            container.mux(packet)

    print(f"  Done! Saved to {output_path}")


def create_test_pattern_video(output_path: str, width: int = 640, height: int = 480,
                               fps: int = 30, duration_sec: float = 2.0):
    """Create a video with frame counter (useful for testing sync)."""
    total_frames = int(fps * duration_sec)

    print(f"\nCreating test pattern video: {output_path}")

    with av.open(output_path, mode="w") as container:
        stream = container.add_stream("libx264", rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = "yuv420p"
        stream.codec_context.time_base = Fraction(1, fps)

        for frame_idx in range(total_frames):
            # Create frame with number overlay (simple blocks pattern)
            img = np.zeros((height, width, 3), dtype=np.uint8)

            # Background color changes each second
            second = frame_idx // fps
            bg_color = [(100, 50, 50), (50, 100, 50), (50, 50, 100)][second % 3]
            img[:] = bg_color

            # Add frame number as binary pattern in top-left
            for bit in range(10):
                if (frame_idx >> bit) & 1:
                    x = 10 + bit * 20
                    img[10:30, x:x+15] = [255, 255, 255]

            # Add progress bar
            progress = frame_idx / total_frames
            bar_width = int(progress * (width - 40))
            img[height-30:height-10, 20:20+bar_width] = [200, 200, 200]

            frame = av.VideoFrame.from_ndarray(img, format="rgb24")
            frame.pts = frame_idx

            for packet in stream.encode(frame):
                container.mux(packet)

        # Flush
        for packet in stream.encode():
            container.mux(packet)

    print(f"  Done! Saved to {output_path}")


def copy_and_modify_video(input_path: str, output_path: str):
    """Read a video, modify frames, and write to new file."""
    print(f"\nCopying and modifying: {input_path} -> {output_path}")

    with av.open(input_path) as input_container:
        in_stream = input_container.streams.video[0]
        fps = float(in_stream.average_rate) if in_stream.average_rate else 30

        with av.open(output_path, mode="w") as output_container:
            out_stream = output_container.add_stream("libx264", rate=fps)
            out_stream.width = in_stream.width
            out_stream.height = in_stream.height
            out_stream.pix_fmt = "yuv420p"

            frame_count = 0
            for frame in input_container.decode(in_stream):
                # Convert to numpy
                rgb = frame.reformat(format="rgb24").to_ndarray()

                # Modify: add red tint
                rgb[:, :, 0] = np.minimum(255, rgb[:, :, 0].astype(np.uint16) + 30)

                # Add frame counter box
                rgb[10:40, 10:100] = [0, 0, 0]  # Black box

                # Convert back
                out_frame = av.VideoFrame.from_ndarray(rgb, format="rgb24")
                out_frame.pts = frame.pts

                for packet in out_stream.encode(out_frame):
                    output_container.mux(packet)

                frame_count += 1
                if frame_count % 30 == 0:
                    print(f"  Processed {frame_count} frames")

            # Flush
            for packet in out_stream.encode():
                output_container.mux(packet)

    print(f"  Done! Processed {frame_count} frames")


def main():
    output_dir = "."
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]

    try:
        # Example 1: Create gradient video
        create_gradient_video(f"{output_dir}/gradient_test.mp4")

        # Example 2: Create test pattern video
        create_test_pattern_video(f"{output_dir}/test_pattern.mp4")

        # Example 3: Copy and modify (if source exists)
        if len(sys.argv) > 2:
            input_video = sys.argv[2]
            copy_and_modify_video(input_video, f"{output_dir}/modified_copy.mp4")

        print("\n" + "="*60)
        print("All videos created successfully!")
        print("="*60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
