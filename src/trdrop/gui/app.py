"""Qt Application wrapper."""

from __future__ import annotations

import sys
import ctypes
from pathlib import Path

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

        # Set AppUserModelID so Windows treats this as a separate app in taskbar
        if sys.platform == "win32":
            my_app_id = "TheAutomatic.TRDrop.v2"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

        icon_path = Path(__file__).resolve().parent.parent.parent.parent / "trdrop.ico"
        if icon_path.exists():
            from PyQt6.QtGui import QIcon
            self._app.setWindowIcon(QIcon(str(icon_path)))

        self._window = MainWindow()

    def run(self) -> int:
        """Run the application. Returns exit code."""
        self._window.show()
        return self._app.exec()

    @property
    def window(self) -> MainWindow:
        return self._window
