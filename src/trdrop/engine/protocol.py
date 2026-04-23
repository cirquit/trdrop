"""Engine protocol for GUI integration.

Defines the state machine and interface for interactive video processing.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, Protocol

import numpy as np

from trdrop.types.metrics import FrameMetrics

if TYPE_CHECKING:
    from pathlib import Path


class EngineState(Enum):
    """Processing engine states."""

    IDLE = auto()        # No sources configured
    READY = auto()       # Sources loaded, ready to process
    PROCESSING = auto()  # Actively processing frames
    PAUSED = auto()      # Processing paused, can seek within processed range
    COMPLETED = auto()   # All frames processed, full seek available
    ERROR = auto()       # Error occurred, check error_message


@dataclass(frozen=True, slots=True)
class EngineProgress:
    """Progress information during processing."""

    current_frame: int
    total_frames: int
    fps: float  # Processing speed
    state: EngineState

    @property
    def progress_pct(self) -> float:
        """Progress as percentage (0-100)."""
        if self.total_frames == 0:
            return 0.0
        return (self.current_frame / self.total_frames) * 100


@dataclass(frozen=True, slots=True)
class SeekResult:
    """Result of seeking to a frame.

    Contains everything needed to render the frame in the GUI.
    """

    frame_idx: int

    # Per-video data
    frames: tuple[np.ndarray, ...]       # Current frames (RGB)
    prev_frames: tuple[np.ndarray, ...]  # Previous frames (for diff viz)
    metrics: tuple[FrameMetrics, ...]    # Analysis results

    # Aggregated metrics for display
    fps_values: tuple[float, ...]        # Current FPS per video
    frametime_values: tuple[float, ...]  # Current frametime per video

    # Plot histories (for rendering plots)
    fps_histories: tuple[list[float], ...]        # FPS history per video
    frametime_histories: tuple[list[float], ...]  # Frametime history per video

    # Composited frame with overlays (from compositor)
    composited_frame: np.ndarray | None = None


# Callback types for GUI integration
OnStateChange = Callable[[EngineState], None]
OnProgress = Callable[[EngineProgress], None]
OnError = Callable[[str], None]
OnFrameProcessed = Callable[[int, FrameMetrics], None]


class InteractiveEngineProtocol(Protocol):
    """Protocol for interactive video processing engine.

    Supports pause/resume, seeking within processed frames, and
    on-demand diff visualization.

    State machine:
        IDLE → READY: configure()
        READY → PROCESSING: start()
        PROCESSING → PAUSED: pause()
        PAUSED → PROCESSING: resume()
        PROCESSING → COMPLETED: (automatic when done)
        PAUSED/COMPLETED → seek available
        Any → IDLE: clear()
        Any → ERROR: on error

    Thread safety:
        - State transitions are thread-safe
        - Callbacks are invoked on the processing thread
        - GUI should use signals/slots to marshal to main thread
    """

    # ===== State Properties =====

    @property
    @abstractmethod
    def state(self) -> EngineState:
        """Current engine state."""
        ...

    @property
    @abstractmethod
    def processed_frames(self) -> int:
        """Number of frames processed so far."""
        ...

    @property
    @abstractmethod
    def total_frames(self) -> int:
        """Total frames to process (0 if not configured)."""
        ...

    @property
    @abstractmethod
    def error_message(self) -> str | None:
        """Error message if state is ERROR, else None."""
        ...

    # ===== Configuration (IDLE state) =====

    @abstractmethod
    def configure(
        self,
        video_paths: list[Path],
        *,
        output_video_path: Path | None = None,
        output_csv_path: Path | None = None,
        analyzer_config: dict | None = None,
    ) -> None:
        """Configure the engine with video sources and outputs.

        Transitions: IDLE → READY

        Args:
            video_paths: Paths to input video files
            output_video_path: Optional path for video export
            output_csv_path: Optional path for CSV export
            analyzer_config: Optional analyzer configuration

        Raises:
            InvalidStateError: If not in IDLE state
            ConfigurationError: If videos cannot be loaded
        """
        ...

    # ===== Processing Control =====

    @abstractmethod
    def start(self) -> None:
        """Start processing from the beginning.

        Transitions: READY → PROCESSING

        Processing runs in a background thread. Use callbacks
        or poll state/progress for updates.

        Raises:
            InvalidStateError: If not in READY state
        """
        ...

    @abstractmethod
    def pause(self) -> None:
        """Pause processing.

        Transitions: PROCESSING → PAUSED

        Pausing allows seeking within already-processed frames.

        Raises:
            InvalidStateError: If not in PROCESSING state
        """
        ...

    @abstractmethod
    def resume(self) -> None:
        """Resume processing from where it was paused.

        Transitions: PAUSED → PROCESSING

        Raises:
            InvalidStateError: If not in PAUSED state
        """
        ...

    @abstractmethod
    def stop(self) -> None:
        """Stop processing and return to READY state.

        Transitions: PROCESSING/PAUSED → READY

        Clears all processed results. Use clear() to fully reset.

        Raises:
            InvalidStateError: If not in PROCESSING or PAUSED state
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all state and return to IDLE.

        Transitions: Any → IDLE

        Releases all resources, clears processed results.
        """
        ...

    # ===== Seeking (PAUSED/COMPLETED states) =====

    @abstractmethod
    def seek(self, frame_idx: int) -> SeekResult:
        """Seek to a specific frame and return render data.

        Available in: PAUSED, COMPLETED

        Args:
            frame_idx: Frame index to seek to (0-based)

        Returns:
            SeekResult with frames, metrics, and plot histories

        Raises:
            InvalidStateError: If not in PAUSED or COMPLETED state
            IndexError: If frame_idx >= processed_frames or < 0
        """
        ...

    @abstractmethod
    def get_diff_visualization(
        self,
        frame_idx: int,
        video_idx: int = 0,
    ) -> np.ndarray:
        """Get diff visualization for a frame (computed on demand).

        Available in: PAUSED, COMPLETED

        Args:
            frame_idx: Frame index
            video_idx: Which video (for multi-video)

        Returns:
            Diff visualization as RGB numpy array

        Raises:
            InvalidStateError: If not in PAUSED or COMPLETED state
            IndexError: If frame_idx or video_idx out of range
        """
        ...

    # ===== Callbacks =====

    @abstractmethod
    def set_on_state_change(self, callback: OnStateChange | None) -> None:
        """Set callback for state changes."""
        ...

    @abstractmethod
    def set_on_progress(self, callback: OnProgress | None) -> None:
        """Set callback for progress updates (called periodically)."""
        ...

    @abstractmethod
    def set_on_error(self, callback: OnError | None) -> None:
        """Set callback for errors."""
        ...

    @abstractmethod
    def set_on_frame_processed(self, callback: OnFrameProcessed | None) -> None:
        """Set callback for each processed frame (for live preview)."""
        ...


class InvalidStateError(Exception):
    """Raised when an operation is not valid for the current state."""

    def __init__(
        self,
        operation: str,
        current_state: EngineState,
        allowed_states: list[EngineState],
    ) -> None:
        allowed = ", ".join(s.name for s in allowed_states)
        super().__init__(
            f"Cannot {operation} in state {current_state.name}. "
            f"Allowed states: {allowed}"
        )
        self.operation = operation
        self.current_state = current_state
        self.allowed_states = allowed_states


class ConfigurationError(Exception):
    """Raised when engine configuration fails."""

    pass
