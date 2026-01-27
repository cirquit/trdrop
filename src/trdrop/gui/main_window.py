"""Main application window."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from trdrop.engine import EngineState, InteractiveEngine
from trdrop.gui.widgets.state_indicator import StateIndicator


class MainWindow(QMainWindow):
    """Main application window with InteractiveEngine integration."""

    def __init__(self) -> None:
        super().__init__()

        # Engine
        self._engine = InteractiveEngine(self)
        self._engine.state_changed.connect(self._on_state_changed)
        self._engine.progress.connect(self._on_progress)
        self._engine.error.connect(self._on_error)

        # Video paths (before loading into engine)
        self._pending_videos: list[Path] = []

        self._setup_ui()
        self._setup_menu()
        self._update_controls()

        self.setAcceptDrops(True)

    def _setup_ui(self) -> None:
        """Setup the main UI layout."""
        self.setWindowTitle("TRDrop v2")
        self.setMinimumSize(600, 400)
        self.resize(800, 500)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Control bar (below menu)
        self._control_bar = self._create_control_bar()
        layout.addWidget(self._control_bar)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Main content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)

        # Video list display
        self._video_list_label = QLabel(
            "No videos loaded.\nDrag and drop video files or use + to add."
        )
        self._video_list_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_list_label.setStyleSheet("color: #888; font-size: 14px;")
        content_layout.addWidget(self._video_list_label, stretch=1)

        # Progress display
        self._progress_label = QLabel("")
        self._progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._progress_label.setStyleSheet("font-size: 13px;")
        content_layout.addWidget(self._progress_label)

        layout.addWidget(content, stretch=1)

    def _create_control_bar(self) -> QWidget:
        """Create the control bar with state, video controls, and seek."""
        bar = QWidget()
        bar.setStyleSheet("background-color: #f5f5f5;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(12)

        # State indicator
        self._state_indicator = StateIndicator()
        layout.addWidget(self._state_indicator)

        # Separator
        layout.addWidget(self._create_separator())

        # Video controls
        video_label = QLabel("Videos:")
        video_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(video_label)

        self._add_btn = QPushButton("+")
        self._add_btn.setFixedSize(28, 28)
        self._add_btn.setToolTip("Add video")
        self._add_btn.clicked.connect(self._on_add_video)
        layout.addWidget(self._add_btn)

        self._remove_btn = QPushButton("-")
        self._remove_btn.setFixedSize(28, 28)
        self._remove_btn.setToolTip("Remove last video")
        self._remove_btn.clicked.connect(self._on_remove_video)
        layout.addWidget(self._remove_btn)

        self._video_count_label = QLabel("0")
        self._video_count_label.setStyleSheet("font-weight: bold; min-width: 20px;")
        layout.addWidget(self._video_count_label)

        # Separator
        layout.addWidget(self._create_separator())

        # Processing controls
        self._start_btn = QPushButton("Start")
        self._start_btn.setToolTip("Start processing")
        self._start_btn.clicked.connect(self._on_start)
        layout.addWidget(self._start_btn)

        self._pause_btn = QPushButton("Pause")
        self._pause_btn.setToolTip("Pause processing")
        self._pause_btn.clicked.connect(self._on_pause)
        layout.addWidget(self._pause_btn)

        self._reset_btn = QPushButton("Reset")
        self._reset_btn.setToolTip("Reset engine")
        self._reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(self._reset_btn)

        # Separator
        layout.addWidget(self._create_separator())

        # Seek controls
        seek_label = QLabel("Seek:")
        seek_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(seek_label)

        self._seek_spinbox = QSpinBox()
        self._seek_spinbox.setMinimum(0)
        self._seek_spinbox.setMaximum(0)
        self._seek_spinbox.setFixedWidth(80)
        layout.addWidget(self._seek_spinbox)

        self._seek_btn = QPushButton("Seek")
        self._seek_btn.setToolTip("Seek to frame")
        self._seek_btn.clicked.connect(self._on_seek)
        layout.addWidget(self._seek_btn)

        layout.addStretch()

        return bar

    def _create_separator(self) -> QFrame:
        """Create a vertical separator line."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        return sep

    def _setup_menu(self) -> None:
        """Setup menu bar."""
        menubar = self.menuBar()
        assert menubar is not None

        # File menu
        file_menu = menubar.addMenu("&File")
        assert file_menu is not None

        open_action = QAction("&Add Video...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_add_video)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        assert help_menu is not None

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _update_controls(self) -> None:
        """Update control states based on engine state."""
        state = self._engine.state
        video_count = len(self._pending_videos)

        # Video controls
        can_modify_videos = state == EngineState.IDLE
        self._add_btn.setEnabled(can_modify_videos and video_count < 4)
        self._remove_btn.setEnabled(can_modify_videos and video_count > 0)
        self._video_count_label.setText(str(video_count))

        # Processing controls
        self._start_btn.setEnabled(state == EngineState.READY)
        self._pause_btn.setEnabled(state == EngineState.PROCESSING)
        self._pause_btn.setText("Resume" if state == EngineState.PAUSED else "Pause")
        if state == EngineState.PAUSED:
            self._pause_btn.setEnabled(True)
        self._reset_btn.setEnabled(state != EngineState.IDLE)

        # Seek controls
        can_seek = state in (EngineState.PAUSED, EngineState.COMPLETED)
        self._seek_spinbox.setEnabled(can_seek)
        self._seek_btn.setEnabled(can_seek)
        if can_seek:
            self._seek_spinbox.setMaximum(max(0, self._engine.processed_frames - 1))

        # Update video list display
        self._update_video_list()

    def _update_video_list(self) -> None:
        """Update the video list display."""
        if not self._pending_videos:
            self._video_list_label.setText(
                "No videos loaded.\nDrag and drop video files or use + to add."
            )
            self._video_list_label.setStyleSheet("color: #888; font-size: 14px;")
        else:
            lines = ["Loaded videos:"]
            for i, path in enumerate(self._pending_videos, 1):
                lines.append(f"  {i}. {path.name}")
            self._video_list_label.setText("\n".join(lines))
            self._video_list_label.setStyleSheet("color: #333; font-size: 13px;")

    # === Event Handlers ===

    def _on_state_changed(self, state: EngineState) -> None:
        """Handle engine state change."""
        self._state_indicator.set_state(state)
        self._update_controls()

    def _on_progress(self, current: int, total: int) -> None:
        """Handle processing progress update."""
        pct = (current / total * 100) if total > 0 else 0
        self._progress_label.setText(f"Processing: {current}/{total} frames ({pct:.1f}%)")
        self._state_indicator.set_state(
            EngineState.PROCESSING,
            f"Processing {current}/{total}"
        )

    def _on_error(self, message: str) -> None:
        """Handle engine error."""
        QMessageBox.critical(self, "Processing Error", message)
        self._state_indicator.set_state(EngineState.ERROR, message)

    def _on_add_video(self) -> None:
        """Add a video file."""
        if len(self._pending_videos) >= 4:
            QMessageBox.warning(self, "Limit Reached", "Maximum 4 videos supported.")
            return

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Add Video",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm);;All Files (*)",
        )
        if path:
            self._add_video(Path(path))

    def _add_video(self, path: Path) -> None:
        """Add a video to the pending list."""
        if not path.exists():
            QMessageBox.warning(self, "File Not Found", f"File not found: {path}")
            return

        if len(self._pending_videos) >= 4:
            return

        self._pending_videos.append(path)
        self._update_controls()

        # If we have videos and engine is IDLE, load them
        if self._engine.state == EngineState.IDLE and self._pending_videos:
            self._load_videos()

    def _on_remove_video(self) -> None:
        """Remove the last video."""
        if self._pending_videos and self._engine.state == EngineState.IDLE:
            self._pending_videos.pop()
            self._update_controls()

            # Reload if we still have videos
            if self._pending_videos:
                self._load_videos()

    def _load_videos(self) -> None:
        """Load pending videos into the engine."""
        if not self._pending_videos:
            return

        try:
            result = self._engine.load(list(self._pending_videos))
            self._seek_spinbox.setMaximum(result.total_frames - 1)
            self._progress_label.setText(
                f"Loaded {result.video_count} video(s), {result.total_frames} frames"
            )
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))
            self._pending_videos.clear()
            self._update_controls()

    def _on_start(self) -> None:
        """Start processing."""
        try:
            self._engine.start()
        except Exception as e:
            QMessageBox.critical(self, "Start Error", str(e))

    def _on_pause(self) -> None:
        """Pause or resume processing."""
        try:
            if self._engine.state == EngineState.PROCESSING:
                self._engine.pause()
            elif self._engine.state == EngineState.PAUSED:
                self._engine.resume()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_reset(self) -> None:
        """Reset the engine."""
        self._engine.reset()
        self._pending_videos.clear()
        self._progress_label.setText("")
        self._update_controls()

    def _on_seek(self) -> None:
        """Seek to the specified frame."""
        frame_idx = self._seek_spinbox.value()
        try:
            result = self._engine.seek(frame_idx)
            # Display seek result info
            metrics_info = []
            for i, m in enumerate(result.metrics):
                dup = "dup" if m.is_duplicate else "unique"
                metrics_info.append(f"V{i+1}: {dup}")

            fps_info = [f"{fps:.1f}" for fps in result.fps_values]

            self._progress_label.setText(
                f"Frame {frame_idx}: {', '.join(metrics_info)} | "
                f"FPS: {', '.join(fps_info)}"
            )
        except Exception as e:
            QMessageBox.warning(self, "Seek Error", str(e))

    def _on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About TRDrop",
            "TRDrop v2.0.0\n\n"
            "Video framerate and frametime analysis tool.\n\n"
            "Drop video files to analyze their real framerate.",
        )

    # === Drag and Drop ===

    def dragEnterEvent(self, a0: QDragEnterEvent | None) -> None:
        """Accept video file drops."""
        if a0 is None:
            return

        mime = a0.mimeData()
        if mime is not None and mime.hasUrls():
            a0.acceptProposedAction()

    def dropEvent(self, a0: QDropEvent | None) -> None:
        """Handle dropped files."""
        if a0 is None:
            return

        mime = a0.mimeData()
        if mime is None:
            return

        video_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
        for url in mime.urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() in video_exts:
                self._add_video(path)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Clean up on close."""
        self._engine.reset()
        super().closeEvent(event)
