"""Tests for MainWindow GUI parameter wiring."""

from __future__ import annotations

import sys

import pytest
from PyQt6.QtWidgets import QApplication

from trdrop.gui.main_window import MainWindow

pytestmark = pytest.mark.gui


@pytest.fixture
def qapp() -> QApplication:
    """Create or reuse QApplication for widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_frametime_checkbox_defaults_to_hidden(qapp: QApplication) -> None:
    """Frametime checkbox mirrors the default preset."""
    window = MainWindow()

    assert window._frametime_cb.isChecked() is False
    assert window._preset_config.rendering.frametime_plot.visible is False

    window.close()


def test_frametime_checkbox_updates_preset(qapp: QApplication) -> None:
    """Toggling frametime checkbox updates preset config."""
    window = MainWindow()

    window._frametime_cb.setChecked(True)
    assert window._preset_config.rendering.frametime_plot.visible is True

    window._frametime_cb.setChecked(False)
    assert window._preset_config.rendering.frametime_plot.visible is False

    window.close()
