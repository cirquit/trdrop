"""Frame pattern generators for test videos.

These patterns create visually distinct frames that can be used to verify:
- Frame difference detection (unique frames should be detected as different)
- Duplicate detection (repeated frames should be detected as same)
- Tear detection (horizontal discontinuities should be detected)

Each pattern function takes (content_index, height, width, seed) and returns
an RGB numpy array of shape (height, width, 3) with dtype uint8.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

import numpy as np


class PatternType(Enum):
    """Available frame content patterns."""

    # Basic patterns
    SOLID = "solid"  # Solid color, changes each content frame
    GRADIENT = "gradient"  # Horizontal gradient, shifts each content frame
    COUNTER = "counter"  # Binary counter pattern (machine-verifiable)
    NOISE = "noise"  # Deterministic noise based on content index

    # Motion patterns (for complex difference detection)
    SWIRL = "swirl"  # Rotating swirl pattern
    BLOCKS = "blocks"  # Grid of blocks, subset changes each frame
    CHECKERBOARD = "checkerboard"  # Alternating pattern that shifts
    BARS = "bars"  # Vertical bars that move horizontally

    # Tear simulation patterns
    HORIZONTAL_BANDS = "horizontal_bands"  # Bands for tear detection
    TEAR_SIMULATION = "tear_simulation"  # Simulates actual screen tears


@dataclass
class TearInfo:
    """Information about a simulated tear in a frame."""

    row: int  # Row where tear occurs
    top_content_index: int  # Content index of top portion
    bottom_content_index: int  # Content index of bottom portion


class PatternGenerator(Protocol):
    """Protocol for pattern generator functions."""

    def __call__(
        self, content_index: int, height: int, width: int, rng: np.random.Generator
    ) -> np.ndarray: ...


def generate_solid(
    content_index: int, height: int, width: int, rng: np.random.Generator
) -> np.ndarray:
    """Solid color that changes each content frame using golden ratio for distribution."""
    hue = (content_index * 0.618033988749895) % 1.0

    # HSV to RGB (S=1, V=1)
    i = int(hue * 6)
    f = hue * 6 - i
    q = 1 - f

    colors = [
        (1, f, 0),
        (q, 1, 0),
        (0, 1, f),
        (0, q, 1),
        (f, 0, 1),
        (1, 0, q),
    ]
    r, g, b = colors[i % 6]

    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = [int(r * 255), int(g * 255), int(b * 255)]
    return img


def generate_gradient(
    content_index: int, height: int, width: int, rng: np.random.Generator
) -> np.ndarray:
    """Horizontal gradient that shifts each content frame."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    shift = (content_index * width // 10) % width

    for x in range(width):
        val = int(255 * ((x + shift) % width) / width)
        img[:, x] = [val, val, val]
    return img


def generate_counter(
    content_index: int, height: int, width: int, rng: np.random.Generator
) -> np.ndarray:
    """Binary counter - each frame has unique bit pattern for verification."""
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Background changes slightly
    bg_val = 32 + (content_index % 4) * 16
    img[:, :] = [bg_val, bg_val, bg_val]

    # Binary bits in top portion
    bit_width = min(w // 20, 32) if (w := width) > 40 else 2
    bit_height = min(h // 10, 32) if (h := height) > 20 else 2
    margin = max(2, min(10, width // 64))

    for bit in range(min(16, (width - margin * 2) // (bit_width + 2))):
        if (content_index >> bit) & 1:
            x_start = margin + bit * (bit_width + 2)
            x_end = min(x_start + bit_width, width - margin)
            y_end = min(margin + bit_height, height - margin)
            img[margin:y_end, x_start:x_end] = [255, 255, 255]

    return img


def generate_noise(
    content_index: int, height: int, width: int, rng: np.random.Generator
) -> np.ndarray:
    """Deterministic noise pattern - completely different each frame."""
    # Use content_index to seed a local RNG for reproducibility
    local_rng = np.random.default_rng(rng.integers(0, 2**31) + content_index)
    return local_rng.integers(0, 256, size=(height, width, 3), dtype=np.uint8)


def generate_swirl(
    content_index: int, height: int, width: int, rng: np.random.Generator
) -> np.ndarray:
    """Rotating swirl pattern - creates complex motion between frames."""
    img = np.zeros((height, width, 3), dtype=np.uint8)

    cx, cy = width // 2, height // 2
    angle_offset = content_index * 0.2  # Rotate 0.2 radians per frame

    y_coords, x_coords = np.ogrid[:height, :width]
    dx = x_coords - cx
    dy = y_coords - cy

    distance = np.sqrt(dx**2 + dy**2)
    angle = np.arctan2(dy, dx) + angle_offset + distance * 0.02

    # Create swirl pattern
    val = ((np.sin(angle * 5) + 1) * 127).astype(np.uint8)
    img[:, :, 0] = val
    img[:, :, 1] = ((np.cos(angle * 3) + 1) * 127).astype(np.uint8)
    img[:, :, 2] = ((np.sin(angle * 7 + distance * 0.05) + 1) * 127).astype(np.uint8)

    return img


def generate_blocks(
    content_index: int, height: int, width: int, rng: np.random.Generator
) -> np.ndarray:
    """Grid of blocks where a subset changes each frame."""
    img = np.zeros((height, width, 3), dtype=np.uint8)

    block_size = max(16, min(height, width) // 8)
    rows = height // block_size
    cols = width // block_size

    local_rng = np.random.default_rng(rng.integers(0, 2**31))

    for row in range(rows):
        for col in range(cols):
            # Each block has a "change frequency" - some change every frame,
            # some every 2 frames, some every 4, etc.
            block_id = row * cols + col
            change_freq = 1 << (block_id % 4)  # 1, 2, 4, 8

            # Determine block color based on content_index and change frequency
            block_content = content_index // change_freq
            block_rng = np.random.default_rng(local_rng.integers(0, 2**31) + block_content)

            color = block_rng.integers(50, 256, size=3, dtype=np.uint8)

            y1 = row * block_size
            y2 = min(y1 + block_size, height)
            x1 = col * block_size
            x2 = min(x1 + block_size, width)

            img[y1:y2, x1:x2] = color

    return img


def generate_checkerboard(
    content_index: int, height: int, width: int, rng: np.random.Generator
) -> np.ndarray:
    """Checkerboard pattern that shifts position each frame."""
    img = np.zeros((height, width, 3), dtype=np.uint8)

    square_size = max(8, min(height, width) // 16)
    shift_x = (content_index * square_size // 2) % (square_size * 2)
    shift_y = (content_index * square_size // 3) % (square_size * 2)

    for y in range(height):
        for x in range(width):
            # Determine if this pixel is on a "white" or "black" square
            check_x = (x + shift_x) // square_size
            check_y = (y + shift_y) // square_size
            is_white = (check_x + check_y) % 2 == 0

            img[y, x] = [200, 200, 200] if is_white else [50, 50, 50]

    return img


def generate_bars(
    content_index: int, height: int, width: int, rng: np.random.Generator
) -> np.ndarray:
    """Vertical bars that move horizontally - good for detecting motion."""
    img = np.zeros((height, width, 3), dtype=np.uint8)

    bar_width = max(4, width // 20)
    offset = (content_index * bar_width // 2) % (bar_width * 2)

    for x in range(width):
        bar_index = (x + offset) // bar_width
        if bar_index % 2 == 0:
            val = 200
        else:
            val = 50
        img[:, x] = [val, val, val]

    return img


def generate_horizontal_bands(
    content_index: int, height: int, width: int, rng: np.random.Generator
) -> np.ndarray:
    """Horizontal bands - useful for tear detection testing."""
    img = np.zeros((height, width, 3), dtype=np.uint8)

    num_bands = 8
    band_height = height // num_bands

    for band in range(num_bands):
        y1 = band * band_height
        y2 = min(y1 + band_height, height)

        # Each band has different color that changes based on content_index
        hue = ((band + content_index * 0.1) * 0.125) % 1.0
        i = int(hue * 6)
        f = hue * 6 - i
        colors = [(1, f, 0), (1 - f, 1, 0), (0, 1, f), (0, 1 - f, 1), (f, 0, 1), (1, 0, 1 - f)]
        r, g, b = colors[i % 6]

        img[y1:y2, :] = [int(r * 200 + 55), int(g * 200 + 55), int(b * 200 + 55)]

    return img


# Pattern function registry
PATTERN_GENERATORS: dict[PatternType, PatternGenerator] = {
    PatternType.SOLID: generate_solid,
    PatternType.GRADIENT: generate_gradient,
    PatternType.COUNTER: generate_counter,
    PatternType.NOISE: generate_noise,
    PatternType.SWIRL: generate_swirl,
    PatternType.BLOCKS: generate_blocks,
    PatternType.CHECKERBOARD: generate_checkerboard,
    PatternType.BARS: generate_bars,
    PatternType.HORIZONTAL_BANDS: generate_horizontal_bands,
    # TEAR_SIMULATION is handled specially in the generator
}


def embed_content_index(img: np.ndarray, content_index: int) -> None:
    """Embed content index as a small visual marker (bottom-right, in-place)."""
    h, w = img.shape[:2]

    box_size = min(20, h // 10, w // 10)
    margin = max(2, min(5, w // 100))

    if box_size < 4 or margin < 1:
        return  # Too small to embed

    # Encode index as grayscale (wraps at 256)
    val = content_index % 256
    y1, y2 = h - margin - box_size, h - margin
    x1, x2 = w - margin - box_size, w - margin

    img[y1:y2, x1:x2] = [val, val, val]

    # White border
    if y1 > 0 and x1 > 0:
        img[y1 - 1, x1 - 1 : x2 + 1] = [255, 255, 255]
        img[y2, x1 - 1 : x2 + 1] = [255, 255, 255]
        img[y1 - 1 : y2 + 1, x1 - 1] = [255, 255, 255]
        img[y1 - 1 : y2 + 1, x2] = [255, 255, 255]
