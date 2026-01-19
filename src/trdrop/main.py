"""TRDrop v2 entry point."""

from __future__ import annotations


def main() -> int:
    """Main entry point for TRDrop. Returns 0 on success."""
    from trdrop.gui.app import TRDropApp

    app = TRDropApp()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
