"""Test video configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Self

import numpy as np
import yaml

from tests.testkit.distributions import (
    FloatOrDist,
    from_serializable,
    resolve,
    to_serializable,
)
from tests.testkit.patterns import PatternType


class CodecType(Enum):
    """Supported output codecs."""

    H264 = "libx264"
    MPEG4 = "mpeg4"
    RAW = "rawvideo"


@dataclass
class TearSpec:
    """Specification for a simulated screen tear."""

    frame_index: int
    row: int

    def to_dict(self) -> dict:
        return {"frame_index": self.frame_index, "row": self.row}

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(frame_index=data["frame_index"], row=data["row"])


@dataclass
class VideoConfig:
    """
    Configuration for generating test videos.

    The key concept: container_fps is the recording framerate (fixed),
    content_fps is how often the actual image changes (simulates game FPS).
    Both can be fixed values or distributions (sampled once at generation time).
    """

    container_fps: FloatOrDist = 60
    content_fps: FloatOrDist = 30
    duration_sec: FloatOrDist = 2.0

    width: int = 640
    height: int = 480

    pattern: PatternType = PatternType.SOLID
    codec: CodecType = CodecType.H264
    pixel_format: str = "yuv420p"

    frame_pattern: list[int] | None = None
    tears: list[TearSpec] = field(default_factory=list)

    seed: int = 42

    def resolve(self, rng: np.random.Generator | None = None) -> ResolvedVideoConfig:
        """Resolve all distributions to concrete values."""
        if rng is None:
            rng = np.random.default_rng(self.seed)

        container = int(resolve(self.container_fps, rng))
        content = int(resolve(self.content_fps, rng))
        duration = resolve(self.duration_sec, rng)

        return ResolvedVideoConfig(
            container_fps=container,
            content_fps=content,
            duration_sec=duration,
            width=self.width,
            height=self.height,
            pattern=self.pattern,
            codec=self.codec,
            pixel_format=self.pixel_format,
            frame_pattern=self.frame_pattern,
            tears=self.tears,
            seed=self.seed,
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        """Load configuration from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)

        if "pattern" in data:
            data["pattern"] = PatternType(data["pattern"])
        if "codec" in data:
            data["codec"] = CodecType(data["codec"])
        if "tears" in data:
            data["tears"] = [TearSpec.from_dict(t) for t in data["tears"]]

        for key in ["container_fps", "content_fps", "duration_sec"]:
            if key in data:
                data[key] = from_serializable(data[key])

        return cls(**data)

    def to_yaml(self, path: str | Path) -> None:
        """Save configuration to YAML file."""
        data = {
            "container_fps": to_serializable(self.container_fps),
            "content_fps": to_serializable(self.content_fps),
            "duration_sec": to_serializable(self.duration_sec),
            "width": self.width,
            "height": self.height,
            "pattern": self.pattern.value,
            "codec": self.codec.value,
            "pixel_format": self.pixel_format,
            "seed": self.seed,
        }
        if self.frame_pattern is not None:
            data["frame_pattern"] = self.frame_pattern
        if self.tears:
            data["tears"] = [t.to_dict() for t in self.tears]

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)


@dataclass
class ResolvedVideoConfig:
    """VideoConfig with all distributions resolved to concrete values."""

    container_fps: int
    content_fps: int
    duration_sec: float

    width: int
    height: int

    pattern: PatternType
    codec: CodecType
    pixel_format: str

    frame_pattern: list[int] | None
    tears: list[TearSpec]

    seed: int

    def __post_init__(self) -> None:
        if self.content_fps > self.container_fps:
            raise ValueError(
                f"content_fps ({self.content_fps}) cannot exceed "
                f"container_fps ({self.container_fps})"
            )
        if self.content_fps <= 0 or self.container_fps <= 0:
            raise ValueError("FPS values must be positive")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Resolution must be positive")
        if self.duration_sec <= 0:
            raise ValueError("Duration must be positive")

    @property
    def total_frames(self) -> int:
        return int(self.container_fps * self.duration_sec)

    @property
    def frames_per_content(self) -> float:
        return self.container_fps / self.content_fps

    @property
    def total_unique_frames(self) -> int:
        return int(self.content_fps * self.duration_sec)

    def get_content_index(self, frame_index: int) -> int:
        if self.frame_pattern is not None:
            return self.frame_pattern[frame_index % len(self.frame_pattern)]
        return int(frame_index / self.frames_per_content)

    def is_duplicate(self, frame_index: int) -> bool:
        if frame_index == 0:
            return False
        return self.get_content_index(frame_index) == self.get_content_index(frame_index - 1)

    def get_tear_at_frame(self, frame_index: int) -> TearSpec | None:
        for tear in self.tears:
            if tear.frame_index == frame_index:
                return tear
        return None

    def to_dict(self) -> dict:
        """Serialize to dict for JSON storage."""
        return {
            "container_fps": self.container_fps,
            "content_fps": self.content_fps,
            "duration_sec": self.duration_sec,
            "width": self.width,
            "height": self.height,
            "pattern": self.pattern.value,
            "codec": self.codec.value,
            "pixel_format": self.pixel_format,
            "frame_pattern": self.frame_pattern,
            "tears": [t.to_dict() for t in self.tears],
            "seed": self.seed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Deserialize from dict."""
        return cls(
            container_fps=data["container_fps"],
            content_fps=data["content_fps"],
            duration_sec=data["duration_sec"],
            width=data["width"],
            height=data["height"],
            pattern=PatternType(data["pattern"]),
            codec=CodecType(data["codec"]),
            pixel_format=data["pixel_format"],
            frame_pattern=data.get("frame_pattern"),
            tears=[TearSpec.from_dict(t) for t in data.get("tears", [])],
            seed=data["seed"],
        )
