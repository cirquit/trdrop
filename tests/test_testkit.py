"""Tests for the test video generation kit."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from tests.testkit import (
    CodecType,
    Constant,
    Gaussian,
    PatternType,
    TearSpec,
    Uniform,
    VideoConfig,
    VideoGenerator,
    VideoGroundTruth,
)


class TestDistributions:
    """Tests for value distributions."""

    def test_constant_always_returns_same_value(self) -> None:
        rng = np.random.default_rng(42)
        dist = Constant(30.0)
        samples = [dist.sample(rng) for _ in range(10)]
        assert all(s == 30.0 for s in samples)

    def test_gaussian_samples_around_mean(self) -> None:
        rng = np.random.default_rng(42)
        dist = Gaussian(mean=30.0, std=0.2)
        samples = [dist.sample(rng) for _ in range(1000)]
        assert 29.5 < np.mean(samples) < 30.5
        assert np.std(samples) < 0.5

    def test_gaussian_clamps_negative(self) -> None:
        rng = np.random.default_rng(42)
        dist = Gaussian(mean=0.1, std=1.0)
        samples = [dist.sample(rng) for _ in range(100)]
        assert all(s >= 0.0 for s in samples)

    def test_uniform_samples_in_range(self) -> None:
        rng = np.random.default_rng(42)
        dist = Uniform(low=10.0, high=20.0)
        samples = [dist.sample(rng) for _ in range(100)]
        assert all(10.0 <= s <= 20.0 for s in samples)

    def test_distribution_roundtrip(self) -> None:
        from tests.testkit.distributions import Distribution

        for dist in [Constant(30.0), Gaussian(30.0, 0.5), Uniform(10.0, 20.0)]:
            restored = Distribution.from_dict(dist.to_dict())
            assert type(restored) is type(dist)


class TestVideoConfig:
    """Tests for VideoConfig."""

    def test_default_config_resolves(self) -> None:
        config = VideoConfig()
        resolved = config.resolve()
        assert resolved.container_fps == 60
        assert resolved.content_fps == 30
        assert resolved.total_frames == 120
        assert resolved.total_unique_frames == 60
        assert resolved.frames_per_content == 2.0

    def test_content_index_mapping(self) -> None:
        config = VideoConfig(container_fps=60, content_fps=30).resolve()
        assert config.get_content_index(0) == 0
        assert config.get_content_index(1) == 0
        assert config.get_content_index(2) == 1
        assert config.get_content_index(3) == 1
        assert config.get_content_index(4) == 2

    def test_duplicate_detection(self) -> None:
        config = VideoConfig(container_fps=60, content_fps=30).resolve()
        assert not config.is_duplicate(0)
        assert config.is_duplicate(1)
        assert not config.is_duplicate(2)
        assert config.is_duplicate(3)

    def test_no_duplicates_when_fps_match(self) -> None:
        config = VideoConfig(container_fps=30, content_fps=30).resolve()
        for i in range(10):
            assert config.get_content_index(i) == i
            if i > 0:
                assert not config.is_duplicate(i)

    def test_validation_content_exceeds_container(self) -> None:
        with pytest.raises(ValueError, match=r"cannot exceed"):
            VideoConfig(container_fps=30, content_fps=60).resolve()

    def test_custom_frame_pattern(self) -> None:
        config = VideoConfig(
            container_fps=10,
            content_fps=5,
            frame_pattern=[0, 0, 0, 1, 1, 2, 2, 2, 2, 3],
        ).resolve()
        assert config.get_content_index(0) == 0
        assert config.get_content_index(1) == 0
        assert config.get_content_index(2) == 0
        assert config.get_content_index(3) == 1
        assert config.get_content_index(4) == 1
        assert config.get_content_index(5) == 2

    def test_yaml_roundtrip(self, tmp_path: Path) -> None:
        config = VideoConfig(
            container_fps=60,
            content_fps=20,
            duration_sec=3.0,
            width=1920,
            height=1080,
            pattern=PatternType.COUNTER,
        )
        yaml_path = tmp_path / "test_config.yaml"
        config.to_yaml(yaml_path)

        loaded = VideoConfig.from_yaml(yaml_path)
        assert loaded.container_fps == config.container_fps
        assert loaded.content_fps == config.content_fps
        assert loaded.duration_sec == config.duration_sec
        assert loaded.width == config.width
        assert loaded.height == config.height
        assert loaded.pattern == config.pattern

    def test_yaml_with_distribution(self, tmp_path: Path) -> None:
        config = VideoConfig(
            container_fps=60,
            content_fps=Gaussian(30.0, 0.2),
            duration_sec=2.0,
        )
        yaml_path = tmp_path / "test_dist.yaml"
        config.to_yaml(yaml_path)

        loaded = VideoConfig.from_yaml(yaml_path)
        assert isinstance(loaded.content_fps, Gaussian)

    def test_config_with_tears(self) -> None:
        config = VideoConfig(
            container_fps=60,
            content_fps=30,
            tears=[TearSpec(frame_index=5, row=240)],
        )
        resolved = config.resolve()
        assert len(resolved.tears) == 1
        assert resolved.get_tear_at_frame(5) is not None
        assert resolved.get_tear_at_frame(0) is None


class TestVideoGenerator:
    """Tests for VideoGenerator."""

    def test_iter_frames_count(self) -> None:
        config = VideoConfig(container_fps=30, content_fps=30, duration_sec=1.0)
        gen = VideoGenerator(config)
        frames = list(gen.iter_frames())
        assert len(frames) == 30

    def test_iter_frames_metadata(self) -> None:
        config = VideoConfig(container_fps=60, content_fps=30, duration_sec=0.5)
        gen = VideoGenerator(config)
        frames = list(gen.iter_frames())

        assert frames[0].index == 0
        assert frames[0].content_index == 0
        assert not frames[0].is_duplicate

        assert frames[1].index == 1
        assert frames[1].content_index == 0
        assert frames[1].is_duplicate

        assert frames[2].index == 2
        assert frames[2].content_index == 1
        assert not frames[2].is_duplicate

    def test_duplicate_frames_are_identical(self) -> None:
        config = VideoConfig(container_fps=60, content_fps=30, duration_sec=0.5)
        gen = VideoGenerator(config)
        frames = list(gen.iter_frames())

        assert np.array_equal(frames[0].array, frames[1].array)
        assert not np.array_equal(frames[0].array, frames[2].array)

    def test_unique_frames_are_different(self) -> None:
        config = VideoConfig(
            container_fps=30,
            content_fps=30,
            duration_sec=0.5,
            pattern=PatternType.SOLID,
        )
        gen = VideoGenerator(config)
        frames = list(gen.iter_frames())

        for i in range(len(frames) - 1):
            assert not np.array_equal(frames[i].array, frames[i + 1].array)

    def test_frame_array_shape(self) -> None:
        config = VideoConfig(width=640, height=480)
        gen = VideoGenerator(config)
        frame = next(gen.iter_frames())
        assert frame.array.shape == (480, 640, 3)
        assert frame.array.dtype == np.uint8

    def test_deterministic_generation(self) -> None:
        config = VideoConfig(seed=12345)
        gen1 = VideoGenerator(config)
        gen2 = VideoGenerator(config)

        frames1 = list(gen1.iter_frames())
        frames2 = list(gen2.iter_frames())

        for f1, f2 in zip(frames1, frames2):
            assert np.array_equal(f1.array, f2.array)

    def test_write_video_file(self, tmp_path: Path) -> None:
        config = VideoConfig(
            container_fps=30,
            content_fps=30,
            duration_sec=0.5,
            width=320,
            height=240,
            codec=CodecType.MPEG4,
        )
        gen = VideoGenerator(config)
        output_path = tmp_path / "test_video.mp4"
        ground_truth = gen.write(output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0
        assert isinstance(ground_truth, VideoGroundTruth)

        import av

        with av.open(str(output_path)) as container:
            stream = container.streams.video[0]
            assert stream.width == 320
            assert stream.height == 240
            frame_count = sum(1 for _ in container.decode(video=0))
            assert frame_count == 15

    def test_expected_analysis(self) -> None:
        config = VideoConfig(container_fps=60, content_fps=30, duration_sec=2.0)
        gen = VideoGenerator(config)
        expected = gen.get_expected_analysis()

        assert expected["container_fps"] == 60
        assert expected["expected_real_fps"] == 30
        assert expected["total_frames"] == 120
        assert expected["unique_frames"] == 60
        assert expected["duplicate_frames"] == 60

    def test_all_pattern_types(self) -> None:
        for pattern in PatternType:
            config = VideoConfig(
                container_fps=10,
                content_fps=10,
                duration_sec=0.2,
                pattern=pattern,
            )
            gen = VideoGenerator(config)
            frames = list(gen.iter_frames())
            assert len(frames) == 2

            for frame in frames:
                assert frame.array.shape == (480, 640, 3)
                assert frame.array.dtype == np.uint8


class TestGroundTruth:
    """Tests for ground truth generation and embedding."""

    def test_ground_truth_generation(self) -> None:
        config = VideoConfig(container_fps=60, content_fps=30, duration_sec=0.5)
        gen = VideoGenerator(config)
        truth = gen.generate_ground_truth()

        assert len(truth.frames) == 30
        assert truth.duplicate_count == 15
        assert truth.unique_count == 15

    def test_ground_truth_with_tears(self) -> None:
        config = VideoConfig(
            container_fps=10,
            content_fps=5,
            duration_sec=1.0,
            tears=[TearSpec(frame_index=3, row=240)],
        )
        gen = VideoGenerator(config)
        truth = gen.generate_ground_truth()

        assert truth.tear_count == 1
        torn_frame = truth.frames[3]
        assert torn_frame.tear is not None
        assert torn_frame.tear.row == 240

    def test_ground_truth_json_roundtrip(self) -> None:
        config = VideoConfig(container_fps=30, content_fps=30, duration_sec=0.2)
        gen = VideoGenerator(config)
        truth = gen.generate_ground_truth()

        json_str = truth.to_json()
        restored = VideoGroundTruth.from_json(json_str)

        assert len(restored.frames) == len(truth.frames)
        assert restored.config.container_fps == truth.config.container_fps

    def test_ground_truth_embedded_in_video(self, tmp_path: Path) -> None:
        config = VideoConfig(
            container_fps=30,
            content_fps=15,
            duration_sec=0.5,
            width=320,
            height=240,
            codec=CodecType.MPEG4,
        )
        gen = VideoGenerator(config)
        output_path = tmp_path / "test_with_truth.mp4"
        original_truth = gen.write(output_path)

        import av

        with av.open(str(output_path)) as container:
            restored_truth = VideoGroundTruth.from_container(container)

        assert restored_truth.duplicate_count == original_truth.duplicate_count
        assert len(restored_truth.frames) == len(original_truth.frames)
