"""Value distributions for test video configuration."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeAlias

import numpy as np


class Distribution(ABC):
    """Base class for value distributions."""

    @abstractmethod
    def sample(self, rng: np.random.Generator) -> float:
        """Sample a value from this distribution."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize to dict for JSON storage."""

    @classmethod
    def from_dict(cls, data: dict) -> Distribution:
        """Deserialize from dict."""
        dist_type = data.get("type", "constant")
        if dist_type == "constant":
            return Constant(value=data["value"])
        elif dist_type == "gaussian":
            return Gaussian(mean=data["mean"], std=data["std"])
        elif dist_type == "uniform":
            return Uniform(low=data["low"], high=data["high"])
        else:
            raise ValueError(f"Unknown distribution type: {dist_type}")


@dataclass
class Constant(Distribution):
    """Always returns the same value."""

    value: float

    def sample(self, rng: np.random.Generator) -> float:
        return self.value

    def to_dict(self) -> dict:
        return {"type": "constant", "value": self.value}


@dataclass
class Gaussian(Distribution):
    """Samples from a normal distribution, clamped to non-negative."""

    mean: float
    std: float = 0.2

    def sample(self, rng: np.random.Generator) -> float:
        return max(0.0, rng.normal(self.mean, self.std))

    def to_dict(self) -> dict:
        return {"type": "gaussian", "mean": self.mean, "std": self.std}


@dataclass
class Uniform(Distribution):
    """Samples uniformly between low and high."""

    low: float
    high: float

    def sample(self, rng: np.random.Generator) -> float:
        return rng.uniform(self.low, self.high)

    def to_dict(self) -> dict:
        return {"type": "uniform", "low": self.low, "high": self.high}


# Type alias for config fields that accept either a fixed value or distribution
FloatOrDist: TypeAlias = float | Distribution


def resolve(value: FloatOrDist, rng: np.random.Generator) -> float:
    """Resolve a value or distribution to a concrete float."""
    if isinstance(value, Distribution):
        return value.sample(rng)
    return value


def to_serializable(value: FloatOrDist) -> float | dict:
    """Convert to JSON-serializable form."""
    if isinstance(value, Distribution):
        return value.to_dict()
    return value


def from_serializable(data: float | dict) -> FloatOrDist:
    """Parse from JSON-serialized form."""
    if isinstance(data, dict):
        return Distribution.from_dict(data)
    return data
