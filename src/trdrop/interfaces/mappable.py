"""Pure transformation interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

In = TypeVar("In", contravariant=True)
Out = TypeVar("Out", covariant=True)


class Mappable(ABC, Generic[In, Out]):
    """
    Pure transformation from In to Out.

    Contract:
    - Pure: No side effects
    - Deterministic: Same input always produces same output
    - Non-mutating: Input is never modified

    Implementations may hold configuration state (thresholds, etc.)
    but must not modify it during map().
    """

    @abstractmethod
    def map(self, input: In) -> Out:
        """Transform input to output."""
