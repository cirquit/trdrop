"""Ground truth data for test videos."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Self

from tests.testkit.config import ResolvedVideoConfig
from tests.testkit.patterns import TearInfo

if TYPE_CHECKING:
    from av.container import InputContainer


@dataclass
class FrameGroundTruth:
    """Ground truth for a single frame."""

    index: int
    content_index: int
    is_duplicate: bool
    tear: TearInfo | None = None

    def to_dict(self) -> dict:
        result: dict = {
            "index": self.index,
            "content_index": self.content_index,
            "is_duplicate": self.is_duplicate,
        }
        if self.tear is not None:
            result["tear"] = {
                "row": self.tear.row,
                "top_content_index": self.tear.top_content_index,
                "bottom_content_index": self.tear.bottom_content_index,
            }
        return result

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        tear = None
        if "tear" in data:
            t = data["tear"]
            tear = TearInfo(
                row=t["row"],
                top_content_index=t["top_content_index"],
                bottom_content_index=t["bottom_content_index"],
            )
        return cls(
            index=data["index"],
            content_index=data["content_index"],
            is_duplicate=data["is_duplicate"],
            tear=tear,
        )


@dataclass
class VideoGroundTruth:
    """Complete ground truth for a generated video."""

    config: ResolvedVideoConfig
    frames: list[FrameGroundTruth] = field(default_factory=list)

    @property
    def duplicate_count(self) -> int:
        return sum(1 for f in self.frames if f.is_duplicate)

    @property
    def unique_count(self) -> int:
        return len(self.frames) - self.duplicate_count

    @property
    def tear_count(self) -> int:
        return sum(1 for f in self.frames if f.tear is not None)

    def to_dict(self) -> dict:
        return {
            "config": self.config.to_dict(),
            "frames": [f.to_dict() for f in self.frames],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            config=ResolvedVideoConfig.from_dict(data["config"]),
            frames=[FrameGroundTruth.from_dict(f) for f in data["frames"]],
        )

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_container(cls, container: "InputContainer") -> Self:
        """Extract ground truth from an open av.InputContainer's metadata."""
        if "comment" not in container.metadata:
            raise ValueError("No ground truth found in container metadata")
        return cls.from_json(container.metadata["comment"])

    def write_json(self, path: str | Path) -> None:
        """Write ground truth to a JSON file."""
        Path(path).write_text(self.to_json())

    @classmethod
    def read_json(cls, path: str | Path) -> Self:
        """Read ground truth from a JSON file."""
        return cls.from_json(Path(path).read_text())
