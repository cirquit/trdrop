"""Test video generator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np

from tests.testkit.config import ResolvedVideoConfig, VideoConfig
from tests.testkit.ground_truth import FrameGroundTruth, VideoGroundTruth
from tests.testkit.patterns import (
    PATTERN_GENERATORS,
    PatternType,
    TearInfo,
    generate_horizontal_bands,
)


@dataclass
class GeneratedFrame:
    """A generated test frame with metadata."""

    index: int
    content_index: int
    is_duplicate: bool
    array: np.ndarray
    tear_info: TearInfo | None = None

    @property
    def expected_different_from_previous(self) -> bool:
        return not self.is_duplicate


class VideoGenerator:
    """Generate test videos with known properties."""

    def __init__(self, config: VideoConfig | ResolvedVideoConfig) -> None:
        if isinstance(config, VideoConfig):
            self._config = config.resolve()
        else:
            self._config = config
        self._rng = np.random.default_rng(self._config.seed)
        self._content_frames: dict[int, np.ndarray] = {}

    @property
    def config(self) -> ResolvedVideoConfig:
        return self._config

    def _get_content_frame(self, content_index: int) -> np.ndarray:
        if content_index not in self._content_frames:
            self._content_frames[content_index] = self._generate_pattern(content_index)
        return self._content_frames[content_index]

    def _generate_pattern(self, content_index: int) -> np.ndarray:
        h, w = self._config.height, self._config.width
        pattern = self._config.pattern

        if pattern == PatternType.TEAR_SIMULATION:
            img = generate_horizontal_bands(content_index, h, w, self._rng)
        elif pattern in PATTERN_GENERATORS:
            generator = PATTERN_GENERATORS[pattern]
            img = generator(content_index, h, w, self._rng)
        else:
            raise ValueError(f"Unknown pattern type: {pattern}")

        return img

    def _apply_tear(
        self, frame_index: int, content_index: int, base_img: np.ndarray
    ) -> tuple[np.ndarray, TearInfo | None]:
        """Apply tear effect if specified for this frame."""
        tear_spec = self._config.get_tear_at_frame(frame_index)
        if tear_spec is None:
            return base_img, None

        prev_content_index = content_index - 1 if content_index > 0 else 0
        if prev_content_index == content_index:
            return base_img, None

        h, w = self._config.height, self._config.width
        row = tear_spec.row

        top_img = self._get_content_frame(prev_content_index)
        bottom_img = base_img

        torn_img = np.zeros((h, w, 3), dtype=np.uint8)
        torn_img[:row, :] = top_img[:row, :]
        torn_img[row:, :] = bottom_img[row:, :]

        tear_info = TearInfo(
            row=row,
            top_content_index=prev_content_index,
            bottom_content_index=content_index,
        )
        return torn_img, tear_info

    def iter_frames(self) -> Iterator[GeneratedFrame]:
        """Iterate over all frames in the video."""
        for frame_idx in range(self._config.total_frames):
            content_idx = self._config.get_content_index(frame_idx)
            is_dup = self._config.is_duplicate(frame_idx)
            base_array = self._get_content_frame(content_idx)

            array, tear_info = self._apply_tear(frame_idx, content_idx, base_array)

            yield GeneratedFrame(
                index=frame_idx,
                content_index=content_idx,
                is_duplicate=is_dup,
                array=array,
                tear_info=tear_info,
            )

    def generate_ground_truth(self) -> VideoGroundTruth:
        """Generate ground truth for all frames."""
        frames = []
        for gen_frame in self.iter_frames():
            frames.append(
                FrameGroundTruth(
                    index=gen_frame.index,
                    content_index=gen_frame.content_index,
                    is_duplicate=gen_frame.is_duplicate,
                    tear=gen_frame.tear_info,
                )
            )
        return VideoGroundTruth(config=self._config, frames=frames)

    def write(
        self, path: str | Path, embed_ground_truth: bool = True
    ) -> VideoGroundTruth:
        """Write the test video to a file. Returns ground truth."""
        import av
        from av.video import VideoStream

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        ground_truth = self.generate_ground_truth()

        with av.open(str(path), mode="w") as container:
            if embed_ground_truth:
                container.metadata["comment"] = ground_truth.to_json()

            stream = container.add_stream(
                self._config.codec.value, rate=self._config.container_fps
            )
            assert isinstance(stream, VideoStream)
            stream.width = self._config.width
            stream.height = self._config.height
            stream.pix_fmt = self._config.pixel_format

            for gen_frame in self.iter_frames():
                frame = av.VideoFrame.from_ndarray(gen_frame.array, format="rgb24")
                for packet in stream.encode(frame):
                    container.mux(packet)

            for packet in stream.encode():
                container.mux(packet)

        return ground_truth

    def get_expected_analysis(self) -> dict:
        """Return expected analysis results for verification."""
        ground_truth = self.generate_ground_truth()
        return {
            "container_fps": self._config.container_fps,
            "expected_real_fps": self._config.content_fps,
            "total_frames": self._config.total_frames,
            "unique_frames": ground_truth.unique_count,
            "duplicate_frames": ground_truth.duplicate_count,
            "tear_count": ground_truth.tear_count,
            "duration_sec": self._config.duration_sec,
        }
