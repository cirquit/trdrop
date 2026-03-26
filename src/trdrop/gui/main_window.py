"""Main application window."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QImage, QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from trdrop.config import PresetConfig, load_preset, save_preset
from trdrop.engine import EngineState, InteractiveEngine
from trdrop.gui.widgets.state_indicator import StateIndicator
from trdrop.profiling.profiler import reset_profiler

FLUENT_STYLE = """
QMainWindow {
    background-color: #f3f3f3;
}
QFrame#sidebar, QFrame#bottom_bar {
    background-color: #f8f8f8;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}
QLabel {
    color: #1c1c1c;
    font-size: 13px;
    font-family: "-apple-system", "BlinkMacSystemFont", "Segoe UI Variable Text", "Segoe UI", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", "Source Han Sans SC", "Noto Sans SC", sans-serif;
}
QPushButton {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
    border-radius: 6px;
    padding: 6px 14px;
    color: #1c1c1c;
    font-size: 13px;
    font-family: "-apple-system", "BlinkMacSystemFont", "Segoe UI Variable Text", "Segoe UI", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", "Source Han Sans SC", "Noto Sans SC", sans-serif;
}
QPushButton:hover {
    background-color: #f5f5f5;
}
QPushButton:pressed {
    background-color: #ebebeb;
    color: #666666;
}
QPushButton:disabled {
    background-color: #f9f9f9;
    color: #a0a0a0;
    border: 1px solid #e0e0e0;
}
QPushButton#primary_btn {
    background-color: #0060df;
    color: white;
    border: 1px solid #0050ba;
    font-weight: bold;
}
QPushButton#primary_btn:hover {
    background-color: #0050ba;
}
QPushButton#primary_btn:pressed {
    background-color: #004095;
    color: #e0e0e0;
}
QPushButton#primary_btn:disabled {
    background-color: #8cb6f5;
    border: 1px solid #8cb6f5;
    color: #ffffff;
}
QSpinBox, QDoubleSpinBox {
    font-family: "-apple-system", "BlinkMacSystemFont", "Segoe UI Variable Text", "Segoe UI", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", "Source Han Sans SC", "Noto Sans SC", sans-serif;
    min-height: 24px;
}
QCheckBox {
    font-size: 13px;
    font-family: "-apple-system", "BlinkMacSystemFont", "Segoe UI Variable Text", "Segoe UI", "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", "Source Han Sans SC", "Noto Sans SC", sans-serif;
}
"""


class MainWindow(QMainWindow):
    """Main application window with InteractiveEngine integration."""

    def __init__(self) -> None:
        super().__init__()
        self._lang = "en"
        self._ignore_frames = False

        # Engine
        self._engine = InteractiveEngine(self)

        # Icon
        from trdrop.utils.frozen import icon_path
        _icon = icon_path()
        if _icon is not None:
            self.setWindowIcon(QIcon(str(_icon)))

        self._engine.state_changed.connect(self._on_state_changed)
        self._engine.progress.connect(self._on_progress)
        self._engine.error.connect(self._on_error)
        self._engine.frame_ready.connect(self._on_frame_ready)

        # Video paths (before loading into engine)
        self._pending_videos: list[Path] = []

        # Optional export paths
        self._output_csv_path: Path | None = None
        self._output_video_path: Path | None = None
        self._processing_start_time: float | None = None
        self._preset_config: PresetConfig = PresetConfig()

        self._setup_ui()
        self._setup_shortcuts()
        self._update_controls()
        self._retranslate_ui()

        self.setAcceptDrops(True)

    # ================================================================
    # UI Setup
    # ================================================================

    def _setup_ui(self) -> None:
        """Setup the main UI layout."""
        self.setWindowTitle("TRDrop v2.1")
        self.setMinimumSize(850, 600)
        self.resize(1100, 750)
        self.setStyleSheet(FLUENT_STYLE)

        # Hide the default empty menu bar
        mb = self.menuBar()
        if mb is not None:
            mb.setVisible(False)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # 1. Left Sidebar
        self._sidebar = self._create_sidebar()
        main_layout.addWidget(self._sidebar)

        # 2. Right Content Area (Status + Preview + Bottom Control Bar)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Top Status Row
        status_row = QHBoxLayout()
        status_row.setContentsMargins(4, 8, 4, 4)
        self._state_indicator = StateIndicator()
        self._state_indicator.set_translator(self._t)
        status_row.addWidget(self._state_indicator)

        status_row.addStretch()

        self._progress_label = QLabel("")
        self._progress_label.setStyleSheet("font-size: 13px; color: #555; font-weight: 500;")
        status_row.addWidget(self._progress_label)
        right_layout.addLayout(status_row)

        # Stacked widget: page 0 = text placeholder, page 1 = preview
        self._content_stack = QStackedWidget()
        self._content_stack.setStyleSheet(
            "background-color: #000000; border-radius: 8px;"
        )

        # Page 0: Video list text
        self._video_list_label = QLabel(
            "No videos loaded.\nDrag and drop video files or use + to add."
        )
        self._video_list_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_list_label.setStyleSheet(
            "font-size: 15px; color: #666666; "
            "background-color: #ffffff; border-radius: 8px;"
        )
        self._content_stack.addWidget(self._video_list_label)

        # Page 1: Preview display
        self._preview_label = QLabel()
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setStyleSheet(
            "background-color: #000000; border-radius: 8px;"
        )
        self._preview_label.setMinimumSize(480, 270)
        self._content_stack.addWidget(self._preview_label)

        right_layout.addWidget(self._content_stack, stretch=1)

        # Bottom Control Bar
        self._bottom_bar = self._create_bottom_bar()
        right_layout.addWidget(self._bottom_bar)

        main_layout.addWidget(right_container, stretch=1)

    def _create_sidebar(self) -> QFrame:
        """Create the left sidebar with video input and settings."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(20)

        # --- Section: Videos ---
        video_sec = QVBoxLayout()
        video_sec.setSpacing(10)
        self._v_title = QLabel("Input Videos")
        self._v_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        video_sec.addWidget(self._v_title)

        btn_layout = QHBoxLayout()
        self._add_btn = QPushButton("+ Add Video")
        self._add_btn.setToolTip("Add video")
        self._add_btn.clicked.connect(self._on_add_video)
        btn_layout.addWidget(self._add_btn)

        self._remove_btn = QPushButton("- Remove")
        self._remove_btn.setToolTip("Remove last video")
        self._remove_btn.clicked.connect(self._on_remove_video)
        btn_layout.addWidget(self._remove_btn)
        video_sec.addLayout(btn_layout)



        layout.addLayout(video_sec)
        layout.addWidget(self._create_separator(horizontal=True))

        # --- Section: Parameters ---
        param_sec = QVBoxLayout()
        param_sec.setSpacing(10)
        self._p_title = QLabel("Parameters")
        self._p_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        param_sec.addWidget(self._p_title)


        thresh_layout = QHBoxLayout()
        self._thresh_label = QLabel("Duplicate Threshold:")
        thresh_layout.addWidget(self._thresh_label)
        self._thresh_spinbox = QDoubleSpinBox()
        self._thresh_spinbox.setRange(0.001, 0.100)
        self._thresh_spinbox.setSingleStep(0.005)
        self._thresh_spinbox.setDecimals(3)
        self._thresh_spinbox.setValue(
            self._preset_config.processing.duplicate_threshold
        )
        self._thresh_spinbox.setToolTip(
            "Duplicate Threshold (e.g. 0.02 = 2% pixels changed)"
        )
        self._thresh_spinbox.valueChanged.connect(self._on_thresh_changed)
        thresh_layout.addWidget(self._thresh_spinbox)
        param_sec.addLayout(thresh_layout)

        self._profile_cb = QCheckBox("Generate Profile CSV")
        self._profile_cb.setToolTip(
            "Generate profiling CSV and summary on completion"
        )
        param_sec.addWidget(self._profile_cb)

        layout.addLayout(param_sec)
        layout.addWidget(self._create_separator(horizontal=True))

        # --- Section: Exports & Config ---
        export_sec = QVBoxLayout()
        export_sec.setSpacing(10)
        self._e_title = QLabel("Exports & Config")
        self._e_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        export_sec.addWidget(self._e_title)

        self._csv_btn = QPushButton("📄 Select CSV Output")
        self._csv_btn.setToolTip("Choose CSV export path")
        self._csv_btn.clicked.connect(self._on_pick_csv)
        export_sec.addWidget(self._csv_btn)

        self._video_btn = QPushButton("🎥 Select Video Output")
        self._video_btn.setToolTip("Choose video export path")
        self._video_btn.clicked.connect(self._on_pick_video_export)
        export_sec.addWidget(self._video_btn)

        self._config_btn = QPushButton("⚙️ Preset Config (.yaml)")
        self._config_btn.setToolTip("Load or save overlay preset (YAML)")
        self._config_btn.clicked.connect(self._on_config)
        export_sec.addWidget(self._config_btn)

        layout.addLayout(export_sec)

        layout.addStretch()

        # Bottom row: About + Language toggle
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        self._about_btn = QPushButton("ℹ️ About TRDrop")
        self._about_btn.setStyleSheet(
            "background-color: transparent; border: none; "
            "color: #888888; font-size: 12px; text-align: left;"
        )
        self._about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._about_btn.clicked.connect(self._on_about)
        bottom_row.addWidget(self._about_btn)

        bottom_row.addStretch()

        self._lang_btn = QPushButton("🌐")
        self._lang_btn.setFixedSize(32, 32)
        self._lang_btn.setStyleSheet(
            "background-color: transparent; border: none; "
            "font-size: 18px; padding: 0px;"
        )
        self._lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._lang_btn.setToolTip("Switch language / 切换语言")
        self._lang_btn.clicked.connect(self._toggle_language)
        bottom_row.addWidget(self._lang_btn)

        layout.addLayout(bottom_row)

        return sidebar

    def _create_bottom_bar(self) -> QFrame:
        """Create the bottom bar with execution controls."""
        bar = QFrame()
        bar.setObjectName("bottom_bar")
        bar.setFixedHeight(80)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(24)

        # Center: Playback controls
        center_layout = QHBoxLayout()
        center_layout.setSpacing(16)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._start_btn = QPushButton("▶ Start")
        self._start_btn.setObjectName("primary_btn")
        self._start_btn.setFixedHeight(42)
        self._start_btn.setFixedWidth(110)
        self._start_btn.setToolTip("Start processing")
        self._start_btn.clicked.connect(self._on_start)
        center_layout.addWidget(self._start_btn)

        self._pause_btn = QPushButton("⏸ Pause")
        self._pause_btn.setFixedHeight(42)
        self._pause_btn.setFixedWidth(110)
        self._pause_btn.setToolTip("Pause processing")
        self._pause_btn.clicked.connect(self._on_pause)
        center_layout.addWidget(self._pause_btn)

        self._reset_btn = QPushButton("⏹ Reset")
        self._reset_btn.setFixedHeight(42)
        self._reset_btn.setFixedWidth(110)
        self._reset_btn.setToolTip("Reset engine")
        self._reset_btn.clicked.connect(self._on_reset)
        center_layout.addWidget(self._reset_btn)

        layout.addStretch(1)
        layout.addLayout(center_layout)
        layout.addStretch(1)

        # Right: Seek controls
        right_layout = QHBoxLayout()
        right_layout.setSpacing(8)
        right_layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        self._seek_label_title = QLabel("Seek Frame:")
        right_layout.addWidget(self._seek_label_title)

        self._seek_spinbox = QSpinBox()
        self._seek_spinbox.setMinimum(0)
        self._seek_spinbox.setMaximum(0)
        self._seek_spinbox.setFixedWidth(80)
        right_layout.addWidget(self._seek_spinbox)

        self._seek_btn = QPushButton("Go")
        self._seek_btn.setFixedWidth(60)
        self._seek_btn.setToolTip("Seek to frame")
        self._seek_btn.clicked.connect(self._on_seek)
        right_layout.addWidget(self._seek_btn)

        layout.addLayout(right_layout, stretch=1)

        return bar

    def _create_separator(self, horizontal: bool = False) -> QFrame:
        """Create a separator line."""
        sep = QFrame()
        if horizontal:
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setFixedHeight(1)
            sep.setStyleSheet("background-color: #d1d1d1; border: none;")
        else:
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setFixedWidth(1)
            sep.setStyleSheet("background-color: #d1d1d1; border: none;")
        return sep

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts (replacing removed menu bar)."""
        sc_open = QShortcut(QKeySequence.StandardKey.Open, self)
        sc_open.activated.connect(self._on_add_video)

        sc_quit = QShortcut(QKeySequence.StandardKey.Quit, self)
        sc_quit.activated.connect(self.close)

    # ================================================================
    # Localization
    # ================================================================

    def _t(self, en_text: str, zh_text: str) -> str:
        """Return text based on current language."""
        return zh_text if self._lang == "zh" else en_text

    def _toggle_language(self) -> None:
        """Toggle between English and Chinese."""
        self._lang = "zh" if self._lang == "en" else "en"
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """Update all translatable text based on current language."""
        if not self._pending_videos:
            self._video_list_label.setText(
                self._t(
                    "No videos loaded.\nDrag and drop video files or use + to add.",
                    "尚未加载视频。\n拖入视频文件或点击 + 添加。",
                )
            )

        self._v_title.setText(self._t("Input Videos", "视频源"))
        self._add_btn.setText(self._t("+ Add Video", "+ 添加视频"))
        self._add_btn.setToolTip(self._t("Add video", "添加视频文件"))
        self._remove_btn.setText(self._t("- Remove", "- 移除视频"))
        self._remove_btn.setToolTip(
            self._t("Remove last video", "移除最后一个视频")
        )
        self._p_title.setText(self._t("Parameters", "分析参数"))
        # lang_btn is icon-only, no text to update
        self._thresh_label.setText(
            self._t("Duplicate Threshold:", "重复帧阈值:")
        )
        self._profile_cb.setText(
            self._t("Generate Profile CSV", "生成性能报告")
        )
        self._e_title.setText(
            self._t("Exports & Config", "导出与预设")
        )
        self._about_btn.setText(
            self._t("ℹ️ About TRDrop", "ℹ️ 关于 TRDrop")
        )

        if self._output_csv_path:
            n = self._output_csv_path.name
            self._csv_btn.setText(
                self._t(f"📄 CSV✓ ({n})", f"📄 CSV已选 ({n})")
            )
        else:
            self._csv_btn.setText(
                self._t("📄 Select CSV Output", "📄 选择 CSV 导出路径")
            )

        if self._output_video_path:
            n = self._output_video_path.name
            self._video_btn.setText(
                self._t(f"🎥 Video✓ ({n})", f"🎥 视频已选 ({n})")
            )
        else:
            self._video_btn.setText(
                self._t("🎥 Select Video Output", "🎥 选择视频导出路径")
            )

        self._config_btn.setText(
            self._t("⚙️ Preset Config (.yaml)", "⚙️ 预设配置 (.yaml)")
        )

        self._start_btn.setText(self._t("▶ Start", "▶ 开始"))
        state = self._engine.state
        if state == EngineState.PAUSED:
            self._pause_btn.setText(self._t("▶ Resume", "▶ 继续"))
        else:
            self._pause_btn.setText(self._t("⏸ Pause", "⏸ 暂停"))
        self._reset_btn.setText(self._t("⏹ Reset", "⏹ 重置"))

        self._seek_label_title.setText(
            self._t("Seek Frame:", "跳转到帧:")
        )
        self._seek_btn.setText(self._t("Go", "跳转"))

        self._state_indicator.retranslate()
        self._update_video_list()

    # ================================================================
    # State Management
    # ================================================================

    def _update_controls(self) -> None:
        """Update control states based on engine state."""
        state = self._engine.state
        video_count = len(self._pending_videos)

        # Video/export controls
        can_modify_videos = state in (EngineState.IDLE, EngineState.READY)
        self._add_btn.setEnabled(can_modify_videos and video_count < 4)
        self._remove_btn.setEnabled(can_modify_videos and video_count > 0)
        self._csv_btn.setEnabled(can_modify_videos)
        self._video_btn.setEnabled(can_modify_videos)
        self._config_btn.setEnabled(can_modify_videos)
        self._profile_cb.setEnabled(can_modify_videos)


        # Processing controls
        self._start_btn.setEnabled(state == EngineState.READY)
        self._pause_btn.setEnabled(state == EngineState.PROCESSING)
        self._pause_btn.setText(
            self._t("▶ Resume", "▶ 继续")
            if state == EngineState.PAUSED
            else self._t("⏸ Pause", "⏸ 暂停")
        )
        if state == EngineState.PAUSED:
            self._pause_btn.setEnabled(True)
        self._reset_btn.setEnabled(state != EngineState.IDLE)

        # Seek controls
        can_seek = state in (EngineState.PAUSED, EngineState.COMPLETED)
        self._seek_spinbox.setEnabled(can_seek)
        self._seek_btn.setEnabled(can_seek)
        if can_seek:
            self._seek_spinbox.setMaximum(
                max(0, self._engine.processed_frames - 1)
            )

        # Update video list display
        self._update_video_list()

    def _update_video_list(self) -> None:
        """Update the video list display."""
        if not self._pending_videos:
            self._video_list_label.setText(
                self._t(
                    "No videos loaded.\nDrag and drop video files or use + to add.",
                    "尚未加载视频。\n拖入视频文件或点击 + 添加。",
                )
            )
            self._video_list_label.setEnabled(False)
        else:
            lines = [self._t("Loaded videos:", "已加载:")]
            for i, path in enumerate(self._pending_videos, 1):
                lines.append(f"  {i}. {path.name}")
            self._video_list_label.setText("\n".join(lines))
            self._video_list_label.setEnabled(True)

    # ================================================================
    # Event Handlers
    # ================================================================

    def _on_state_changed(self, state: EngineState) -> None:
        """Handle engine state change."""
        self._state_indicator.set_state(state)
        self._update_controls()
        # Switch to text view when idle
        if state == EngineState.IDLE:
            self._content_stack.setCurrentIndex(0)

    def _on_progress(self, current: int, total: int) -> None:
        """Handle processing progress update."""
        pct = (current / total * 100) if total > 0 else 0
        # Calculate ETA
        eta_text = ""
        if self._processing_start_time is not None and current > 0:
            elapsed = time.time() - self._processing_start_time
            rate = current / elapsed  # frames per second
            remaining = (total - current) / rate if rate > 0 else 0
            if remaining < 60:
                eta_text = f" | ETA: {remaining:.0f}s"
            elif remaining < 3600:
                eta_text = f" | ETA: {remaining / 60:.1f}min"
            else:
                eta_text = f" | ETA: {remaining / 3600:.1f}h"
            eta_text += f" ({rate:.0f} fps)"
        # Export destinations
        exports = []
        if self._output_csv_path is not None:
            exports.append(f"CSV: {self._output_csv_path.name}")
        if self._output_video_path is not None:
            exports.append(f"Video: {self._output_video_path.name}")
        export_text = f" | Export: {', '.join(exports)}" if exports else ""
        self._progress_label.setText(
            self._t(
                f"Processing: {current}/{total} ({pct:.1f}%){eta_text}{export_text}",
                f"处理进度: {current}/{total} ({pct:.1f}%){eta_text}{export_text}",
            )
        )
        self._state_indicator.set_state(
            EngineState.PROCESSING,
            self._t(
                f"Processing {current}/{total}",
                f"处理中 {current}/{total}",
            ),
        )

    def _on_error(self, message: str) -> None:
        """Handle engine error."""
        QMessageBox.critical(self, "Processing Error", message)
        self._state_indicator.set_state(EngineState.ERROR, message)

    def _on_frame_ready(self, frame: object) -> None:
        """Handle live preview frame from processing thread."""
        if self._ignore_frames:
            return
        if not isinstance(frame, np.ndarray):
            return
        self._show_frame(frame)

    def _show_frame(self, frame: np.ndarray) -> None:
        """Display a composited frame in the preview area."""
        h, w = frame.shape[:2]
        bytes_per_line = 3 * w
        image = QImage(
            frame.tobytes(), w, h, bytes_per_line,
            QImage.Format.Format_RGB888,
        )
        pixmap = QPixmap.fromImage(image)
        # Scale to fit preview label while preserving aspect ratio
        label_size = self._preview_label.size()
        scaled = pixmap.scaled(
            label_size, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._preview_label.setPixmap(scaled)
        self._content_stack.setCurrentIndex(1)

    def _on_add_video(self) -> None:
        """Add video file(s)."""
        if len(self._pending_videos) >= 4:
            QMessageBox.warning(
                self, "Limit Reached", "Maximum 4 videos supported."
            )
            return

        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Add Video(s)",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm);;All Files (*)",
        )
        for path in paths:
            if len(self._pending_videos) >= 4:
                break
            self._add_video(Path(path))

    def _add_video(self, path: Path) -> None:
        """Add a video to the pending list."""
        if not path.exists():
            QMessageBox.warning(
                self, "File Not Found", f"File not found: {path}"
            )
            return

        if len(self._pending_videos) >= 4:
            return

        self._pending_videos.append(path)
        self._update_controls()

        # Load/reload engine with current video list
        if self._pending_videos:
            if self._engine.state != EngineState.IDLE:
                self._engine.reset()
            self._load_videos()

    def _on_remove_video(self) -> None:
        """Remove the last video."""
        if self._pending_videos and self._engine.state in (
            EngineState.IDLE, EngineState.READY
        ):
            self._pending_videos.pop()

            if self._engine.state != EngineState.IDLE:
                self._engine.reset()

            self._update_controls()

            # Reload if we still have videos
            if self._pending_videos:
                self._load_videos()

    def _load_videos(self) -> None:
        """Load pending videos into the engine."""
        if not self._pending_videos:
            return

        try:
            result = self._engine.load(
                list(self._pending_videos),
                output_video=self._output_video_path,
                output_csv=self._output_csv_path,
                config=self._preset_config,
            )
            self._seek_spinbox.setMaximum(result.total_frames - 1)
            exports = []
            if self._output_csv_path is not None:
                exports.append(f"CSV: {self._output_csv_path.name}")
            if self._output_video_path is not None:
                exports.append(f"Video: {self._output_video_path.name}")
            export_text = (
                f" | Exports: {', '.join(exports)}" if exports else ""
            )
            self._progress_label.setText(
                self._t(
                    f"Loaded {result.video_count} video(s), "
                    f"{result.total_frames} frames{export_text}",
                    f"成功加载 {result.video_count} 个视频, "
                    f"共 {result.total_frames} 帧{export_text}",
                )
            )
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))
            self._pending_videos.clear()
            self._update_controls()

    def _on_pick_csv(self) -> None:
        """Pick CSV export path (optional)."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose CSV Export Path",
            "trdrop_metrics.csv",
            "CSV Files (*.csv)",
        )
        if path:
            p = Path(path)
            if p.suffix.lower() != ".csv":
                p = p.with_suffix(".csv")
            self._output_csv_path = p
            self._retranslate_ui()
            self._csv_btn.setToolTip(str(p))
            # Reload engine if videos already loaded
            if self._pending_videos and self._engine.state != EngineState.IDLE:
                self._engine.reset()
                self._load_videos()

    def _on_pick_video_export(self) -> None:
        """Pick video export path (optional)."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose Video Export Path",
            "trdrop_output.mp4",
            "Video Files (*.mp4)",
        )
        if path:
            p = Path(path)
            if p.suffix.lower() != ".mp4":
                p = p.with_suffix(".mp4")
            self._output_video_path = p
            self._retranslate_ui()
            self._video_btn.setToolTip(str(p))
            # Reload engine if videos already loaded
            if self._pending_videos and self._engine.state != EngineState.IDLE:
                self._engine.reset()
                self._load_videos()

    def _on_config(self) -> None:
        """Load or save overlay config preset."""
        choice = QMessageBox.question(
            self,
            "Config Preset",
            "Load an existing preset?\n\n"
            "Yes = Load YAML preset\n"
            "No = Save default preset as template",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
        )
        if choice == QMessageBox.StandardButton.Yes:
            path, _ = QFileDialog.getOpenFileName(
                self, "Load Config Preset", "",
                "YAML Files (*.yaml *.yml)",
            )
            if path:
                try:
                    self._preset_config = load_preset(path)
                    self._thresh_spinbox.blockSignals(True)
                    self._thresh_spinbox.setValue(
                        self._preset_config.processing.duplicate_threshold
                    )
                    self._thresh_spinbox.blockSignals(False)
                    self._engine.set_duplicate_threshold(
                        self._preset_config.processing.duplicate_threshold
                    )
                    self._retranslate_ui()
                    self._config_btn.setToolTip(str(path))
                    # Reload engine if videos already loaded
                    if (
                        self._pending_videos
                        and self._engine.state != EngineState.IDLE
                    ):
                        self._engine.reset()
                        self._load_videos()
                except Exception as e:
                    QMessageBox.critical(self, "Config Error", str(e))
        elif choice == QMessageBox.StandardButton.No:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Default Config",
                "trdrop_preset.yaml",
                "YAML Files (*.yaml)",
            )
            if path:
                try:
                    save_preset(self._preset_config, path)
                    QMessageBox.information(
                        self,
                        "Config Saved",
                        f"Default preset saved to:\n{path}\n\n"
                        "Edit this file to customize overlays, "
                        "then load it back.",
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Save Error", str(e))

    def _on_thresh_changed(self, value: float) -> None:
        """Update duplicate threshold in config and engine."""
        self._preset_config.processing.duplicate_threshold = value
        self._engine.set_duplicate_threshold(value)

    def _on_start(self) -> None:
        """Start processing."""
        try:
            import os
            if self._profile_cb.isChecked():
                os.environ["TRDROP_PROFILE"] = "1"
            else:
                os.environ["TRDROP_PROFILE"] = ""
            reset_profiler()

            self._ignore_frames = False
            self._processing_start_time = time.time()
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
        self._ignore_frames = True
        self._engine.reset()
        self._pending_videos.clear()
        self._output_csv_path = None
        self._output_video_path = None
        self._processing_start_time = None
        self._preset_config = PresetConfig()
        self._thresh_spinbox.blockSignals(True)
        self._thresh_spinbox.setValue(
            self._preset_config.processing.duplicate_threshold
        )
        self._thresh_spinbox.blockSignals(False)
        self._retranslate_ui()
        self._progress_label.setText("")
        self._preview_label.clear()
        self._content_stack.setCurrentIndex(0)
        self._update_controls()

    def _on_seek(self) -> None:
        """Seek to the specified frame."""
        frame_idx = self._seek_spinbox.value()
        try:
            result = self._engine.seek(frame_idx)
            # Display composited frame if available
            if result.composited_frame is not None:
                self._show_frame(result.composited_frame)

            # Display seek result info
            metrics_info = []
            for i, m in enumerate(result.metrics):
                dup = "dup" if m.is_duplicate else "unique"
                metrics_info.append(f"V{i+1}: {dup}")

            fps_info = [f"{fps:.1f}" for fps in result.fps_values]

            self._progress_label.setText(
                self._t(
                    f"Frame {frame_idx}: {', '.join(metrics_info)} | "
                    f"FPS: {', '.join(fps_info)}",
                    f"第 {frame_idx} 帧: {', '.join(metrics_info)} | "
                    f"帧率: {', '.join(fps_info)}",
                )
            )
        except Exception as e:
            QMessageBox.warning(self, "Seek Error", str(e))

    def _on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About TRDrop",
            "TRDrop v2.1\n\n"
            "Video framerate and frametime analysis tool.\n\n"
            "Drop video files to analyze their real framerate.",
        )

    # ================================================================
    # Drag and Drop
    # ================================================================

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
