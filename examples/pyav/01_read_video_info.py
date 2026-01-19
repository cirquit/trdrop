#!/usr/bin/env python3
"""
Example 1: Read Video Information

Demonstrates how to open a video file and extract metadata.
"""

import av
import sys


def get_video_info(video_path: str) -> dict:
    """Extract comprehensive video metadata."""
    with av.open(video_path) as container:
        # Get the first video stream
        if not container.streams.video:
            raise ValueError(f"No video stream found in {video_path}")

        stream = container.streams.video[0]

        info = {
            # Container info
            "path": video_path,
            "format": container.format.name,
            "duration_sec": container.duration / 1_000_000 if container.duration else None,
            "bit_rate": container.bit_rate,
            "size_bytes": container.size,

            # Video stream info
            "width": stream.width,
            "height": stream.height,
            "codec": stream.codec_context.name,
            "pix_fmt": stream.format.name if stream.format else None,
            "frame_count": stream.frames,  # 0 if unknown
            "fps_average": float(stream.average_rate) if stream.average_rate else None,
            "fps_base": float(stream.base_rate) if stream.base_rate else None,
            "time_base": str(stream.time_base),

            # Metadata
            "metadata": dict(container.metadata),
        }

        return info


def main():
    if len(sys.argv) < 2:
        print("Usage: python 01_read_video_info.py <video_path>")
        print("\nExample: python 01_read_video_info.py sample.mp4")
        sys.exit(1)

    video_path = sys.argv[1]

    try:
        info = get_video_info(video_path)

        print(f"\n{'='*60}")
        print(f"Video Information: {video_path}")
        print(f"{'='*60}")

        print(f"\nContainer:")
        print(f"  Format:      {info['format']}")
        print(f"  Duration:    {info['duration_sec']:.2f}s" if info['duration_sec'] else "  Duration:    Unknown")
        print(f"  Bitrate:     {info['bit_rate'] / 1000:.0f} kbps" if info['bit_rate'] else "  Bitrate:     Unknown")
        print(f"  Size:        {info['size_bytes'] / 1024 / 1024:.2f} MB" if info['size_bytes'] else "  Size:        Unknown")

        print(f"\nVideo Stream:")
        print(f"  Resolution:  {info['width']}x{info['height']}")
        print(f"  Codec:       {info['codec']}")
        print(f"  Pixel Fmt:   {info['pix_fmt']}")
        print(f"  Frame Count: {info['frame_count'] or 'Unknown'}")
        print(f"  FPS:         {info['fps_average']:.3f}" if info['fps_average'] else "  FPS:         Unknown")
        print(f"  Time Base:   {info['time_base']}")

        if info['metadata']:
            print(f"\nMetadata:")
            for key, value in info['metadata'].items():
                print(f"  {key}: {value}")

        print()

    except FileNotFoundError:
        print(f"Error: File not found: {video_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
