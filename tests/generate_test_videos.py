#!/usr/bin/env python3
"""Generate test videos for experimentation and development."""

from __future__ import annotations

from pathlib import Path

from tests.testkit import (
    PatternType,
    TearSpec,
    VideoConfig,
    VideoGenerator,
)

OUTPUT_DIR = Path(__file__).parent / "videos"


def generate_all() -> None:
    """Generate all test videos."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    configs = [
        # Basic: 60fps container, 60fps content (no duplicates)
        (
            "60fps_native.mp4",
            VideoConfig(
                container_fps=60,
                content_fps=60,
                duration_sec=2.0,
                pattern=PatternType.COUNTER,  # Use COUNTER for reliable detection
            ),
        ),
        # 30fps content in 60fps container (50% duplicates)
        (
            "30fps_in_60fps.mp4",
            VideoConfig(
                container_fps=60,
                content_fps=30,
                duration_sec=2.0,
                pattern=PatternType.COUNTER,
            ),
        ),
        # 24fps content in 60fps container (60% duplicates)
        (
            "24fps_in_60fps.mp4",
            VideoConfig(
                container_fps=60,
                content_fps=24,
                duration_sec=2.0,
                pattern=PatternType.COUNTER,
            ),
        ),
        # Variable framerate simulation (using noise pattern)
        (
            "variable_fps.mp4",
            VideoConfig(
                container_fps=60,
                content_fps=45,  # Average ~45fps
                duration_sec=2.0,
                pattern=PatternType.NOISE,
            ),
        ),
        # Video with tears (uses HORIZONTAL_BANDS for tear visibility)
        (
            "with_tears.mp4",
            VideoConfig(
                container_fps=60,
                content_fps=30,
                duration_sec=2.0,
                pattern=PatternType.TEAR_SIMULATION,
                tears=[
                    TearSpec(frame_index=30, row=240),
                    TearSpec(frame_index=60, row=360),
                    TearSpec(frame_index=90, row=120),
                ],
            ),
        ),
        # Checkerboard pattern for visual verification
        (
            "checkerboard.mp4",
            VideoConfig(
                container_fps=60,
                content_fps=30,
                duration_sec=2.0,
                pattern=PatternType.CHECKERBOARD,
            ),
        ),
        # Gradient pattern
        (
            "gradient.mp4",
            VideoConfig(
                container_fps=60,
                content_fps=30,
                duration_sec=2.0,
                pattern=PatternType.GRADIENT,
            ),
        ),
        # Longer video for timeline testing
        (
            "long_video.mp4",
            VideoConfig(
                container_fps=60,
                content_fps=30,
                duration_sec=10.0,
                pattern=PatternType.COUNTER,
            ),
        ),
    ]

    for filename, config in configs:
        path = OUTPUT_DIR / filename
        print(f"Generating {filename}...")
        generator = VideoGenerator(config)
        generator.write(path)

        analysis = generator.get_expected_analysis()
        print(f"  Container FPS: {analysis['container_fps']}")
        print(f"  Expected real FPS: {analysis['expected_real_fps']}")
        print(f"  Total frames: {analysis['total_frames']}")
        print(
            f"  Unique: {analysis['unique_frames']}, Duplicates: {analysis['duplicate_frames']}"
        )
        if analysis["tear_count"] > 0:
            print(f"  Tears: {analysis['tear_count']}")
        print()

    print(f"Generated {len(configs)} test videos in {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_all()
