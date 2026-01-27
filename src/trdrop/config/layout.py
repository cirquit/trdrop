"""Layout computation for video region positioning.

Defines how multiple videos are arranged within the fused output frame.
"""

from __future__ import annotations

from trdrop.config.types import (
    FrameLayout,
    LayoutConfig,
    LayoutMode,
    VideoRegion,
)


def compute_layout(
    video_count: int,
    config: LayoutConfig,
    output_width: int,
    output_height: int,
) -> FrameLayout:
    """
    Compute frame layout for given number of videos.

    Args:
        video_count: Number of videos to layout
        config: Layout configuration
        output_width: Output frame width in pixels
        output_height: Output frame height in pixels

    Returns:
        FrameLayout with computed regions
    """
    if video_count == 0:
        return FrameLayout(
            regions=(),
            output_width=output_width,
            output_height=output_height,
        )

    spacing = config.spacing
    regions: list[VideoRegion] = []

    match config.mode:
        case LayoutMode.SINGLE:
            # Only first video visible, full frame
            regions.append(VideoRegion(
                index=0,
                x=0.0,
                y=0.0,
                width=1.0,
                height=1.0,
            ))

        case LayoutMode.HORIZONTAL:
            # Side by side
            total_spacing = spacing * (video_count - 1)
            video_width = (1.0 - total_spacing) / video_count
            x = 0.0
            for i in range(video_count):
                regions.append(VideoRegion(
                    index=i,
                    x=x,
                    y=0.0,
                    width=video_width,
                    height=1.0,
                ))
                x += video_width + spacing

        case LayoutMode.VERTICAL:
            # Stacked vertically
            total_spacing = spacing * (video_count - 1)
            video_height = (1.0 - total_spacing) / video_count
            y = 0.0
            for i in range(video_count):
                regions.append(VideoRegion(
                    index=i,
                    x=0.0,
                    y=y,
                    width=1.0,
                    height=video_height,
                ))
                y += video_height + spacing

        case LayoutMode.GRID:
            # 2x2 grid (or less for fewer videos)
            if video_count == 1:
                regions.append(VideoRegion(
                    index=0,
                    x=0.0,
                    y=0.0,
                    width=1.0,
                    height=1.0,
                ))
            elif video_count == 2:
                # Side by side
                video_width = (1.0 - spacing) / 2
                regions.append(VideoRegion(
                    index=0,
                    x=0.0,
                    y=0.0,
                    width=video_width,
                    height=1.0,
                ))
                regions.append(VideoRegion(
                    index=1,
                    x=video_width + spacing,
                    y=0.0,
                    width=video_width,
                    height=1.0,
                ))
            else:
                # 2x2 grid (3 or 4 videos)
                video_width = (1.0 - spacing) / 2
                video_height = (1.0 - spacing) / 2

                positions = [
                    (0.0, 0.0),  # Top-left
                    (video_width + spacing, 0.0),  # Top-right
                    (0.0, video_height + spacing),  # Bottom-left
                    (video_width + spacing, video_height + spacing),  # Bottom-right
                ]

                for i in range(min(video_count, 4)):
                    x, y = positions[i]
                    regions.append(VideoRegion(
                        index=i,
                        x=x,
                        y=y,
                        width=video_width,
                        height=video_height,
                    ))

    return FrameLayout(
        regions=tuple(regions),
        output_width=output_width,
        output_height=output_height,
    )
