"""Interactive engine for GUI integration.

Provides pause/resume/seek capability with Qt signals for GUI updates.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from trdrop.analysis.duplicate import DuplicateDetector
from trdrop.compositor.simple import SimpleCompositor, _VideoState
from trdrop.engine.buffer import ProcessingBuffer
from trdrop.engine.protocol import EngineState, SeekResult
from trdrop.export.streaming_csv import StreamingCSVExporter
from trdrop.export.streaming_video import StreamingVideoExporter
from trdrop.source.sequential import SequentialFrameSource
from trdrop.types.metrics import FrameMetrics
from trdrop.video.reader import PyAVReader

logger = logging.getLogger(__name__)

# Maximum supported videos
MAX_VIDEOS = 4


@dataclass
class LoadResult:
    """Result of loading videos."""

    video_count: int
    total_frames: int
    fps: list[float]
    resolution: list[tuple[int, int]]  # (width, height) per video


class InteractiveEngine(QObject):
    """Interactive video processing engine with pause/seek capability.

    Processes up to 4 videos simultaneously with:
    - Background processing via QThread
    - Pause/resume control
    - Frame-accurate seeking when paused
    - Progress signals for GUI updates

    Usage:
        engine = InteractiveEngine()
        engine.state_changed.connect(on_state_change)
        engine.progress.connect(on_progress)

        engine.load([video1, video2], output_video=out.mp4)
        engine.start()
        # ... processing ...
        engine.pause()
        result = engine.seek(500)  # Get frame 500
        engine.resume()
    """

    # === Signals ===
    state_changed = pyqtSignal(EngineState)
    progress = pyqtSignal(int, int)  # current_frame, total_frames
    error = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        # State
        self._state = EngineState.IDLE
        self._error_message: str | None = None

        # Video sources
        self._readers: list[PyAVReader] = []
        self._sources: list[SequentialFrameSource] = []
        self._video_states: list[_VideoState] = []

        # Processing components
        self._analyzer = DuplicateDetector()
        self._compositor: SimpleCompositor | None = None
        self._buffer: ProcessingBuffer | None = None

        # Export (optional)
        self._video_exporter: StreamingVideoExporter | None = None
        self._csv_exporter: StreamingCSVExporter | None = None

        # Threading
        self._processing_thread: threading.Thread | None = None
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self._pause_event.set()  # Not paused initially

        # Frame tracking
        self._total_frames = 0
        self._current_frame = 0

    # === Properties ===

    @property
    def state(self) -> EngineState:
        """Current engine state."""
        return self._state

    @property
    def processed_frames(self) -> int:
        """Number of frames processed so far."""
        if self._buffer is None:
            return 0
        return self._buffer.processed_count

    @property
    def total_frames(self) -> int:
        """Total frames to process."""
        return self._total_frames

    # === Commands ===

    def load(
        self,
        video_paths: list[Path | str],
        output_video: Path | str | None = None,
        output_csv: Path | str | None = None,
    ) -> LoadResult:
        """Load videos and configure exports.

        Args:
            video_paths: 1-4 video file paths
            output_video: Optional output video path
            output_csv: Optional output CSV path

        Returns:
            LoadResult with video information

        Raises:
            ValueError: If not 1-4 videos or invalid state
            FileNotFoundError: If video file doesn't exist
        """
        if self._state != EngineState.IDLE:
            raise ValueError(f"Cannot load in state {self._state.name}, call reset() first")

        if not video_paths:
            raise ValueError("At least one video path required")

        if len(video_paths) > MAX_VIDEOS:
            raise ValueError(f"Maximum {MAX_VIDEOS} videos supported, got {len(video_paths)}")

        # Convert to Path objects
        paths = [Path(p) for p in video_paths]

        # Verify files exist
        for p in paths:
            if not p.exists():
                raise FileNotFoundError(f"Video file not found: {p}")

        # Open readers
        self._readers = [PyAVReader(p) for p in paths]
        self._sources = [SequentialFrameSource(r) for r in self._readers]

        # Determine total frames (minimum across all videos)
        frame_counts = [r.total_frames for r in self._readers]
        self._total_frames = min(frame_counts) - 1  # -1 because we need pairs

        if len(set(frame_counts)) > 1:
            logger.warning(
                "Videos have different frame counts: %s. "
                "Processing will stop at frame %d.",
                frame_counts,
                self._total_frames,
            )

        # Initialize video states for compositor
        self._video_states = [
            _VideoState(window_size=60, container_fps=r.fps)
            for r in self._readers
        ]

        # Initialize buffer
        self._buffer = ProcessingBuffer(video_count=len(paths))

        # Setup exporters if requested
        if output_video:
            self._video_exporter = StreamingVideoExporter(
                Path(output_video),
                fps=self._readers[0].fps,
            )

        if output_csv:
            self._csv_exporter = StreamingCSVExporter(Path(output_csv))

        # Transition to READY
        self._set_state(EngineState.READY)

        return LoadResult(
            video_count=len(paths),
            total_frames=self._total_frames,
            fps=[r.fps for r in self._readers],
            resolution=[(r.width, r.height) for r in self._readers],
        )

    def start(self) -> None:
        """Start processing in background thread.

        Raises:
            ValueError: If not in READY state
        """
        if self._state != EngineState.READY:
            raise ValueError(f"Cannot start in state {self._state.name}")

        # Reset events
        self._pause_event.set()
        self._stop_event.clear()
        self._current_frame = 0

        # Open exporters
        if self._video_exporter:
            self._video_exporter.open()
        if self._csv_exporter:
            self._csv_exporter.open()

        # Start processing thread
        self._processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True,
        )
        self._processing_thread.start()

        self._set_state(EngineState.PROCESSING)

    def pause(self) -> None:
        """Pause processing.

        Raises:
            ValueError: If not in PROCESSING state
        """
        if self._state != EngineState.PROCESSING:
            raise ValueError(f"Cannot pause in state {self._state.name}")

        self._pause_event.clear()
        self._set_state(EngineState.PAUSED)

    def resume(self) -> None:
        """Resume processing.

        Raises:
            ValueError: If not in PAUSED state
        """
        if self._state != EngineState.PAUSED:
            raise ValueError(f"Cannot resume in state {self._state.name}")

        self._pause_event.set()
        self._set_state(EngineState.PROCESSING)

    def seek(self, frame_idx: int) -> SeekResult:
        """Get frame data at index.

        Only available when PAUSED or COMPLETED.

        Args:
            frame_idx: Frame index to seek to

        Returns:
            SeekResult with frames, metrics, and plot data

        Raises:
            ValueError: If not in PAUSED or COMPLETED state
            IndexError: If frame_idx not yet processed
        """
        if self._state not in (EngineState.PAUSED, EngineState.COMPLETED):
            raise ValueError(f"Cannot seek in state {self._state.name}")

        if self._buffer is None:
            raise ValueError("No data loaded")

        # Get cached snapshot
        snapshot = self._buffer.get(frame_idx)

        # Restore video states
        for i, state in enumerate(self._video_states):
            state.restore(snapshot.video_states[i])

        # Seek video readers and get frames
        frames: list[np.ndarray] = []
        prev_frames: list[np.ndarray] = []

        for reader in self._readers:
            # Allocate buffers for this reader
            frame_shape = (reader.height, reader.width, 3)
            curr_frame = np.empty(frame_shape, dtype=np.uint8)
            prev_frame = np.empty(frame_shape, dtype=np.uint8)

            # Seek to frame_idx to get current frame
            reader.seek(frame_idx)
            if not reader.read(curr_frame):
                raise RuntimeError(f"Failed to read frame {frame_idx}")
            frames.append(curr_frame)

            # Seek to previous frame for diff visualization
            if frame_idx > 0:
                reader.seek(frame_idx - 1)
                if not reader.read(prev_frame):
                    prev_frames.append(curr_frame.copy())  # Fallback
                else:
                    prev_frames.append(prev_frame)
            else:
                prev_frames.append(curr_frame.copy())

        # Extract plot histories from restored states
        fps_histories = tuple(list(s.fps_history) for s in self._video_states)
        frametime_histories = tuple(list(s.frametime_history) for s in self._video_states)

        return SeekResult(
            frame_idx=frame_idx,
            frames=tuple(frames),
            prev_frames=tuple(prev_frames),
            metrics=snapshot.metrics,
            fps_values=tuple(s.smoothed_fps() for s in self._video_states),
            frametime_values=tuple(s.smoothed_frametime() for s in self._video_states),
            fps_histories=fps_histories,
            frametime_histories=frametime_histories,
        )

    def reset(self) -> None:
        """Clear everything and return to IDLE state."""
        # Stop processing if running
        if self._processing_thread and self._processing_thread.is_alive():
            self._stop_event.set()
            self._pause_event.set()  # Unblock if paused
            self._processing_thread.join(timeout=5.0)

        # Close exporters
        if self._video_exporter:
            try:
                self._video_exporter.close()
            except Exception:
                pass
            self._video_exporter = None

        if self._csv_exporter:
            try:
                self._csv_exporter.close()
            except Exception:
                pass
            self._csv_exporter = None

        # Close readers
        for reader in self._readers:
            try:
                reader.close()
            except Exception:
                pass

        # Clear state
        self._readers = []
        self._sources = []
        self._video_states = []
        self._buffer = None
        self._compositor = None
        self._processing_thread = None
        self._total_frames = 0
        self._current_frame = 0
        self._error_message = None

        # Reset events
        self._pause_event.set()
        self._stop_event.clear()

        self._set_state(EngineState.IDLE)

    # === Internal ===

    def _set_state(self, new_state: EngineState) -> None:
        """Set state and emit signal."""
        if self._state != new_state:
            self._state = new_state
            self.state_changed.emit(new_state)

    def _processing_loop(self) -> None:
        """Main processing loop (runs in background thread)."""
        try:
            source_iters = [iter(s) for s in self._sources]

            for frame_idx in range(self._total_frames):
                # Check for stop
                if self._stop_event.is_set():
                    break

                # Check for pause
                self._pause_event.wait()
                if self._stop_event.is_set():
                    break

                # Read frame pairs from all sources
                pairs = []
                for it in source_iters:
                    try:
                        pair = next(it)
                        pairs.append(pair)
                    except StopIteration:
                        break

                if len(pairs) != len(self._sources):
                    break  # Source exhausted

                # Analyze each video
                metrics_list: list[FrameMetrics] = []
                for i, pair in enumerate(pairs):
                    result = self._analyzer.map(pair)
                    metrics = FrameMetrics(
                        frame_index=frame_idx,
                        is_duplicate=result.is_duplicate,
                        diff_ratio=result.diff_ratio,
                    )
                    metrics_list.append(metrics)

                    # Update video state (is_duplicate is always set by DuplicateDetector)
                    self._video_states[i].update(result.is_duplicate or False)

                # Release frame pairs to allow buffer reuse
                for pair in pairs:
                    pair.release()

                # Store snapshot
                if self._buffer is not None:
                    video_snapshots = tuple(s.snapshot() for s in self._video_states)
                    self._buffer.append(
                        frame_idx=frame_idx,
                        metrics=tuple(metrics_list),
                        video_states=video_snapshots,
                    )

                # Export if configured
                # TODO: Integrate compositor for video export

                # Update progress
                self._current_frame = frame_idx
                self.progress.emit(frame_idx + 1, self._total_frames)

            # Processing complete
            if not self._stop_event.is_set():
                self._set_state(EngineState.COMPLETED)

        except Exception as e:
            logger.exception("Processing error")
            self._error_message = str(e)
            self.error.emit(str(e))
            self._set_state(EngineState.ERROR)

        finally:
            # Close exporters
            if self._video_exporter:
                try:
                    self._video_exporter.close()
                except Exception:
                    pass

            if self._csv_exporter:
                try:
                    self._csv_exporter.close()
                except Exception:
                    pass
