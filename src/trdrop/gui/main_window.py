"""Main application window."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSlider,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from trdrop.gui.widgets.fps_plot import FPSPlotWidget
from trdrop.gui.widgets.video_viewport import VideoViewport


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        # TODO: Replace with ProcessingPipeline and PreviewSystem
        self._video_paths: list[Path] = []
        self._current_frame = 0
        self._max_frames = 0

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_shortcuts()

        self.setAcceptDrops(True)

    def _setup_ui(self) -> None:
        """Setup the main UI layout."""
        self.setWindowTitle("TRDrop v2")
        self.setMinimumSize(800, 600)
        self.resize(1280, 720)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Main splitter (video viewports / plot)
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter, stretch=1)

        # Video viewports container
        self._viewport_container = QWidget()
        self._viewport_layout = QHBoxLayout(self._viewport_container)
        self._viewport_layout.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self._viewport_container)

        # Viewports (initially empty)
        self._viewports: list[VideoViewport] = []

        # FPS Plot
        self._fps_plot = FPSPlotWidget()
        splitter.addWidget(self._fps_plot)

        # Set splitter sizes (70% viewports, 30% plot)
        splitter.setSizes([700, 300])

        # Timeline slider
        timeline_widget = QWidget()
        timeline_layout = QHBoxLayout(timeline_widget)
        timeline_layout.setContentsMargins(5, 0, 5, 5)

        self._timeline = QSlider(Qt.Orientation.Horizontal)
        self._timeline.setMinimum(0)
        self._timeline.setMaximum(0)
        self._timeline.valueChanged.connect(self._on_timeline_changed)
        timeline_layout.addWidget(self._timeline)

        layout.addWidget(timeline_widget)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)

        self._progress = QProgressBar()
        self._progress.setMaximumWidth(200)
        self._progress.hide()
        self._status.addPermanentWidget(self._progress)

        self._update_status()

    def _setup_menu(self) -> None:
        """Setup menu bar."""
        menubar = self.menuBar()
        assert menubar is not None

        # File menu
        file_menu = menubar.addMenu("&File")
        assert file_menu is not None

        open_action = QAction("&Open Video...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        export_csv = QAction("Export &CSV...", self)
        export_csv.triggered.connect(self._on_export_csv)
        file_menu.addAction(export_csv)

        export_json = QAction("Export &JSON...", self)
        export_json.triggered.connect(self._on_export_json)
        file_menu.addAction(export_json)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("&View")
        assert view_menu is not None

        # Export menu
        menubar.addMenu("&Export")

        # Help menu
        help_menu = menubar.addMenu("&Help")
        assert help_menu is not None

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Setup toolbar."""
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        # Analysis action
        self._analyze_action = QAction("Analyze", self)
        self._analyze_action.triggered.connect(self._on_analyze)
        self._analyze_action.setEnabled(False)
        toolbar.addAction(self._analyze_action)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        pass  # TODO: Implement keyboard navigation

    def _update_status(self) -> None:
        """Update status bar text."""
        if len(self._video_paths) == 0:
            self._status.showMessage("Drop video files here to begin")
        else:
            frame = self._current_frame
            total = self._max_frames
            videos = len(self._video_paths)
            self._status.showMessage(f"Frame {frame + 1}/{total} | {videos} video(s)")

    def _add_video(self, path: Path) -> None:
        """Add a video to the session."""
        # TODO: Integrate with ProcessingPipeline and PreviewSystem
        try:
            index = len(self._video_paths)
            self._video_paths.append(path)

            # Create viewport
            viewport = VideoViewport(index)
            self._viewports.append(viewport)
            self._viewport_layout.addWidget(viewport)

            # TODO: Get actual frame count from video reader
            # For now, enable analyze button
            self._analyze_action.setEnabled(True)

            self._update_status()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open video: {e}")

    def _on_open(self) -> None:
        """Handle File > Open."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*)",
        )
        if path:
            self._add_video(Path(path))

    def _on_analyze(self) -> None:
        """Run analysis on all videos."""
        # TODO: Integrate with ProcessingPipeline
        self._progress.show()
        self._progress.setValue(0)

        try:
            # TODO: Run ProcessingPipeline and update FPS plot
            pass
        finally:
            self._progress.hide()
            self._update_status()

    def _on_export_csv(self) -> None:
        """Export analysis to CSV."""
        pass  # TODO: Integrate with new Exporter protocol

    def _on_export_json(self) -> None:
        """Export session to JSON."""
        pass  # TODO: Integrate with new Exporter protocol

    def _on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About TRDrop",
            "TRDrop v2.0.0\n\n"
            "Video framerate and frametime analysis tool.\n\n"
            "Drop video files to analyze their real framerate.",
        )

    def _on_timeline_changed(self, value: int) -> None:
        """Handle timeline slider change."""
        # TODO: Integrate with PreviewSystem.seek_to()
        self._current_frame = value
        self._update_status()

    # Drag and drop support

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

        for url in mime.urls():
            path = Path(url.toLocalFile())
            video_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
            if path.suffix.lower() in video_exts:
                self._add_video(path)
