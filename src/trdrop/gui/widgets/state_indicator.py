"""Engine state indicator widget."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPaintEvent
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from trdrop.engine import EngineState

# State colors (macOS-inspired)
STATE_COLORS: dict[EngineState, QColor] = {
    EngineState.IDLE: QColor(142, 142, 147),       # Gray
    EngineState.READY: QColor(0, 122, 255),        # Blue
    EngineState.PROCESSING: QColor(52, 199, 89),   # Green
    EngineState.PAUSED: QColor(255, 149, 0),       # Orange
    EngineState.COMPLETED: QColor(88, 86, 214),    # Purple
    EngineState.ERROR: QColor(255, 59, 48),        # Red
}

STATE_MESSAGES_EN: dict[EngineState, str] = {
    EngineState.IDLE: "No videos loaded",
    EngineState.READY: "Ready to process",
    EngineState.PROCESSING: "Processing...",
    EngineState.PAUSED: "Paused",
    EngineState.COMPLETED: "Complete",
    EngineState.ERROR: "Error",
}

STATE_MESSAGES_ZH: dict[EngineState, str] = {
    EngineState.IDLE: "尚未加载视频",
    EngineState.READY: "就绪",
    EngineState.PROCESSING: "处理中...",
    EngineState.PAUSED: "已暂停",
    EngineState.COMPLETED: "已完成",
    EngineState.ERROR: "出错",
}


class StateCircle(QWidget):
    """A small colored circle indicating state."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = STATE_COLORS[EngineState.IDLE]
        self.setFixedSize(12, 12)

    def set_state(self, state: EngineState) -> None:
        """Update the circle color for the given state."""
        self._color = STATE_COLORS.get(state, STATE_COLORS[EngineState.IDLE])
        self.update()

    def paintEvent(self, a0: QPaintEvent | None) -> None:
        """Paint the circle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self._color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(1, 1, 10, 10)


class StateIndicator(QWidget):
    """Widget showing engine state with colored indicator and text."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state = EngineState.IDLE
        self._translator: Callable[[str, str], str] | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        self._circle = StateCircle()
        layout.addWidget(self._circle)

        self._label = QLabel(STATE_MESSAGES_EN[EngineState.IDLE])
        self._label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self._label)

        layout.addStretch()

    def set_translator(self, t: Callable[[str, str], str]) -> None:
        """Set translation function for bilingual support."""
        self._translator = t

    def _tr(self, en: str, zh: str) -> str:
        if self._translator is not None:
            return self._translator(en, zh)
        return en

    @property
    def state(self) -> EngineState:
        """Current displayed state."""
        return self._state

    def set_state(self, state: EngineState, message: str | None = None) -> None:
        """Update the displayed state.

        Args:
            state: The engine state to display
            message: Optional custom message (uses default if None)
        """
        self._state = state
        self._circle.set_state(state)

        if message is not None:
            self._label.setText(message)
        else:
            en = STATE_MESSAGES_EN.get(state, str(state))
            zh = STATE_MESSAGES_ZH.get(state, en)
            self._label.setText(self._tr(en, zh))

    def retranslate(self) -> None:
        """Re-apply translation to current default state message."""
        en = STATE_MESSAGES_EN.get(self._state, str(self._state))
        zh = STATE_MESSAGES_ZH.get(self._state, en)
        self._label.setText(self._tr(en, zh))
