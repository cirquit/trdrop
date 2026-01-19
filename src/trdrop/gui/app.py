"""Qt Application wrapper."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from trdrop.gui.main_window import MainWindow


class TRDropApp:
    """TRDrop Qt Application."""

    def __init__(self, args: list[str] | None = None) -> None:
        if args is None:
            args = sys.argv

        self._app = QApplication(args)
        self._app.setApplicationName("TRDrop")
        self._app.setApplicationVersion("2.0.0")
        self._app.setOrganizationName("TRDrop")

        self._window = MainWindow()

    def run(self) -> int:
        """Run the application. Returns exit code."""
        self._window.show()
        return self._app.exec()

    @property
    def window(self) -> MainWindow:
        return self._window
