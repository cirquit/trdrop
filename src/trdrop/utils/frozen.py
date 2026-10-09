"""Helpers for PyInstaller frozen builds."""

from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    """Return True when running inside a PyInstaller bundle."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def bundle_dir() -> Path:
    """Return the bundle directory (PyInstaller _MEIPASS or source tree root)."""
    if is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    # Development: project root is 4 levels up from this file
    return Path(__file__).resolve().parent.parent.parent.parent


def icon_path() -> Path | None:
    """Return the app icon path, or None if not found."""
    icon_name = "trdrop_mac.png" if sys.platform == "darwin" else "trdrop.ico"
    p = bundle_dir() / icon_name
    return p if p.exists() else None
