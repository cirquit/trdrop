"""TRDrop Test Video Generation Kit."""

from __future__ import annotations

from tests.testkit.config import CodecType, ResolvedVideoConfig, TearSpec, VideoConfig
from tests.testkit.distributions import Constant, Distribution, Gaussian, Uniform
from tests.testkit.generator import GeneratedFrame, VideoGenerator
from tests.testkit.ground_truth import FrameGroundTruth, VideoGroundTruth
from tests.testkit.patterns import PatternType, TearInfo

__all__ = [
    "CodecType",
    "Constant",
    "Distribution",
    "FrameGroundTruth",
    "Gaussian",
    "GeneratedFrame",
    "PatternType",
    "ResolvedVideoConfig",
    "TearInfo",
    "TearSpec",
    "Uniform",
    "VideoConfig",
    "VideoGenerator",
    "VideoGroundTruth",
]
