#!/usr/bin/env python3
"""
Example 3: Seeking Within Video

Demonstrates how to seek to specific times/frames in a video.
"""

import av
import sys


def seek_to_time(video_path: str, time_seconds: float):
    """Seek to a specific time in the video."""
    with av.open(video_path) as container:
        stream = container.streams.video[0]

        # Calculate PTS from time
        target_pts = int(time_seconds / stream.time_base)

        print(f"Seeking to {time_seconds}s (PTS: {target_pts})")
        print(f"  Time base: {stream.time_base}")

        # Seek (backward=True finds previous keyframe)
        container.seek(target_pts, stream=stream, backward=True)

        # Decode until we reach target frame
        for frame in container.decode(stream):
            print(f"  Got frame PTS={frame.pts}, time={frame.time:.4f}s")

            if frame.pts >= target_pts:
                print(f"\n  Target frame found!")
                print(f"  Size: {frame.width}x{frame.height}")
                print(f"  Format: {frame.format.name}")
                return frame

        print("  Warning: Could not find frame at target time")
        return None


def seek_to_frame_index(video_path: str, frame_index: int):
    """Seek to a specific frame by index (approximate)."""
    with av.open(video_path) as container:
        stream = container.streams.video[0]

        fps = float(stream.average_rate) if stream.average_rate else 30.0
        time_seconds = frame_index / fps

        print(f"\nSeeking to frame index {frame_index} (estimated time: {time_seconds:.3f}s at {fps:.2f} fps)")

        target_pts = int(time_seconds / stream.time_base)
        container.seek(target_pts, stream=stream, backward=True)

        # Count frames until we reach the target
        frame_count = 0
        for frame in container.decode(stream):
            if frame.pts >= target_pts:
                frame_count += 1
                if frame_count == 1:  # First frame at or after target
                    print(f"  Found frame: PTS={frame.pts}, time={frame.time:.4f}s")
                    return frame

        return None


def extract_multiple_frames(video_path: str, times: list):
    """Extract frames at multiple timestamps efficiently."""
    print(f"\nExtracting frames at times: {times}")

    with av.open(video_path) as container:
        stream = container.streams.video[0]

        frames = []
        for t in sorted(times):  # Process in order for efficiency
            target_pts = int(t / stream.time_base)
            container.seek(target_pts, stream=stream, backward=True)

            for frame in container.decode(stream):
                if frame.pts >= target_pts:
                    frames.append({
                        "time": t,
                        "actual_time": frame.time,
                        "pts": frame.pts,
                        "frame": frame,
                    })
                    print(f"  t={t}s -> PTS={frame.pts}, actual_time={frame.time:.4f}s")
                    break

        return frames


def main():
    if len(sys.argv) < 2:
        print("Usage: python 03_seek_frames.py <video_path> [time_seconds]")
        print("\nExample: python 03_seek_frames.py sample.mp4 5.0")
        sys.exit(1)

    video_path = sys.argv[1]
    time_seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0

    try:
        # Get video duration first
        with av.open(video_path) as container:
            duration = container.duration / 1_000_000 if container.duration else None
            fps = float(container.streams.video[0].average_rate) if container.streams.video[0].average_rate else None

        print(f"Video: {video_path}")
        print(f"Duration: {duration:.2f}s" if duration else "Duration: Unknown")
        print(f"FPS: {fps:.2f}" if fps else "FPS: Unknown")
        print("="*60)

        # Test 1: Seek to specific time
        frame = seek_to_time(video_path, time_seconds)

        # Test 2: Seek to frame index
        if fps:
            frame_index = int(time_seconds * fps)
            seek_to_frame_index(video_path, frame_index)

        # Test 3: Extract multiple frames
        if duration:
            times = [0.0, duration * 0.25, duration * 0.5, duration * 0.75]
            times = [t for t in times if t < duration]
            extract_multiple_frames(video_path, times)

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
