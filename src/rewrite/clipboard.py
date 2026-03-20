"""Clipboard utilities — save, capture selection, replace, and restore."""

from __future__ import annotations

import contextlib
import time

import pyperclip
from pynput.keyboard import Controller, Key

CLIPBOARD_DELAY: float = 0.15  # seconds between simulate and read

_kb = Controller()

# Modifiers that might be physically held when the hotkey fires.
_ALL_MODIFIERS = (Key.ctrl_l, Key.ctrl_r, Key.shift_l, Key.shift_r,
                  Key.alt_l, Key.alt_r, Key.cmd)


def _release_all_modifiers() -> None:
    """Release all modifier keys so simulated combos aren't contaminated."""
    for mod in _ALL_MODIFIERS:
        with contextlib.suppress(Exception):
            _kb.release(mod)


def _press_combo(modifier: Key, key: str) -> None:
    """Press a modifier+key combo (e.g. Ctrl+C)."""
    _kb.press(modifier)
    _kb.press(key)
    _kb.release(key)
    _kb.release(modifier)


def save_clipboard() -> str | None:
    """Save current clipboard text content. Returns None if empty or non-text."""
    try:
        return pyperclip.paste()
    except Exception:
        return None


def capture_selection() -> str | None:
    """Simulate Ctrl+C to capture the currently selected text.

    Returns the captured text, or None if nothing was selected.
    Restores the original clipboard content on failure.
    """
    original = save_clipboard()

    # Release any held modifiers from the hotkey combo
    _release_all_modifiers()
    time.sleep(0.05)

    # Clear clipboard so we can detect whether Ctrl+C actually copied something
    pyperclip.copy("")
    time.sleep(0.05)

    _press_combo(Key.ctrl_l, "c")
    time.sleep(CLIPBOARD_DELAY)

    captured = pyperclip.paste()
    if not captured:
        # Nothing was selected — restore what was there before
        if original:
            pyperclip.copy(original)
        return None
    return captured


def replace_selection(text: str) -> None:
    """Replace the current selection by pasting *text* via Ctrl+V."""
    pyperclip.copy(text)
    time.sleep(0.05)
    _press_combo(Key.ctrl_l, "v")
    time.sleep(CLIPBOARD_DELAY)


def restore_clipboard(original: str | None) -> None:
    """Restore the clipboard to its previous content after a short delay."""
    time.sleep(0.3)
    if original is not None:
        pyperclip.copy(original)
    else:
        pyperclip.copy("")
