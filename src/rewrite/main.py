"""Entry point — system-tray icon, global hotkey, and rewrite pipeline."""

from __future__ import annotations

import asyncio
import logging
import sys
import threading
from pathlib import Path

import pystray
from PIL import Image

from rewrite.clipboard import (
    capture_selection,
    replace_selection,
    restore_clipboard,
    save_clipboard,
)
from rewrite.config import load_config
from rewrite.hotkey import HotkeyManager
from rewrite.rewriter import rewrite_text
from rewrite.settings import open_settings

log = logging.getLogger(__name__)


def _base_path() -> Path:
    """Return the base path for bundled assets (PyInstaller or dev)."""
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent.parent


ICON_PATH = _base_path() / "assets" / "icon.ico"

_FALLBACK_COLOR = (66, 133, 244, 255)
_FALLBACK_SIZE = 64


def _get_icon_image() -> Image.Image:
    """Load the tray icon, or create a colored-square fallback."""
    if ICON_PATH.exists():
        return Image.open(ICON_PATH)
    return Image.new(
        "RGBA", (_FALLBACK_SIZE, _FALLBACK_SIZE), _FALLBACK_COLOR,
    )


class RewriteApp:
    """Top-level app: tray icon + hotkey + rewrite pipeline."""

    def __init__(self) -> None:
        self.config = load_config()
        self.hotkey_manager = HotkeyManager()
        self.tray: pystray.Icon | None = None
        self._settings_open = False

    # ------------------------------------------------------------------
    # Rewrite pipeline
    # ------------------------------------------------------------------

    def _on_rewrite(self) -> None:
        """Hotkey callback — run the pipeline on a daemon thread."""
        threading.Thread(
            target=self._rewrite_pipeline, daemon=True,
        ).start()

    def _rewrite_pipeline(self) -> None:
        """Capture -> rewrite -> paste -> restore clipboard."""
        original_clipboard = save_clipboard()
        try:
            text = capture_selection()
            if not text:
                return

            corrected = asyncio.run(rewrite_text(text))

            if corrected and corrected != text:
                replace_selection(corrected)
        except Exception:
            log.exception("Pipeline error")
        finally:
            restore_clipboard(original_clipboard)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _on_settings(
        self,
        icon: pystray.Icon | None = None,
        item: pystray.MenuItem | None = None,
    ) -> None:
        """Open the settings window (once at a time)."""
        if self._settings_open:
            return
        self._settings_open = True

        def _on_save(new_config: dict) -> None:
            self.config = new_config
            self.hotkey_manager.register(
                self.config["hotkey"], self._on_rewrite,
            )

        def _run() -> None:
            try:
                open_settings(on_save=_on_save, icon_path=ICON_PATH)
            finally:
                self._settings_open = False

        threading.Thread(target=_run, daemon=True).start()

    # ------------------------------------------------------------------
    # Quit
    # ------------------------------------------------------------------

    def _on_quit(
        self,
        icon: pystray.Icon | None = None,
        item: pystray.MenuItem | None = None,
    ) -> None:
        """Tear down hotkey listener and stop the tray icon."""
        self.hotkey_manager.unregister()
        if self.tray:
            self.tray.stop()

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Register hotkey, build tray icon, enter event loop."""
        self.hotkey_manager.register(
            self.config["hotkey"], self._on_rewrite,
        )

        menu = pystray.Menu(
            pystray.MenuItem(
                "Rewrite Selection", self._on_rewrite, default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings\u2026", self._on_settings),
            pystray.MenuItem("Quit", self._on_quit),
        )

        self.tray = pystray.Icon(
            name="Retext",
            icon=_get_icon_image(),
            title="Retext",
            menu=menu,
        )
        self.tray.run()


def main() -> None:
    """CLI entry point (``rewrite`` command via pyproject.toml)."""
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    app = RewriteApp()
    app.run()


if __name__ == "__main__":
    main()
