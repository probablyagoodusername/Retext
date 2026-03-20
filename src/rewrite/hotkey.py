"""Global hotkey listener using pynput — register/unregister at runtime."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable

from pynput import keyboard

log = logging.getLogger(__name__)

# Map string modifier names to sets of pynput Key variants they can appear as.
_MOD_VARIANTS: dict[str, set[keyboard.Key]] = {
    "ctrl": {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl},
    "shift": {keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.shift},
    "alt": {keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt},
    "win": {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r},
}

# Reverse lookup: any pynput Key → canonical modifier name.
_KEY_TO_MOD: dict[keyboard.Key, str] = {}
for _name, _variants in _MOD_VARIANTS.items():
    for _v in _variants:
        _KEY_TO_MOD[_v] = _name


def _vk_for_char(char: str) -> int | None:
    """Return the Windows virtual-key code for a single character."""
    return ord(char.upper())


def _parse_hotkey(
    hotkey_str: str,
) -> tuple[frozenset[str], int]:
    """Parse 'ctrl+shift+r' into canonical modifier names and a VK code."""
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    modifiers: set[str] = set()
    vk: int | None = None

    for part in parts:
        if part in _MOD_VARIANTS:
            modifiers.add(part)
        else:
            vk = _vk_for_char(part)

    if vk is None:
        msg = f"No trigger key found in hotkey: {hotkey_str}"
        raise ValueError(msg)

    return frozenset(modifiers), vk


class HotkeyManager:
    """Manages a single global hotkey that can be swapped at runtime."""

    _DEBOUNCE_SECS = 0.5

    def __init__(self) -> None:
        self._current_hotkey: str | None = None
        self._callback: Callable[[], None] | None = None
        self._listener: keyboard.Listener | None = None
        self._modifiers: frozenset[str] = frozenset()
        self._trigger_vk: int | None = None
        self._active_mods: set[str] = set()
        self._last_fire: float = 0.0

    def _on_press(
        self, key: keyboard.Key | keyboard.KeyCode | None,
    ) -> None:
        """Track pressed keys and fire callback on hotkey match."""
        if key is None:
            return

        # Track modifier state
        if isinstance(key, keyboard.Key):
            mod = _KEY_TO_MOD.get(key)
            if mod:
                self._active_mods.add(mod)
            return

        # Non-modifier key — check for hotkey match
        if self._trigger_vk is None or self._callback is None:
            return

        vk = getattr(key, "vk", None)
        now = time.monotonic()
        if (
            vk == self._trigger_vk
            and self._modifiers <= self._active_mods
            and now - self._last_fire > self._DEBOUNCE_SECS
        ):
            self._last_fire = now
            log.info("Hotkey triggered: %s", self._current_hotkey)
            threading.Thread(target=self._callback, daemon=True).start()

    def _on_release(
        self, key: keyboard.Key | keyboard.KeyCode | None,
    ) -> None:
        """Track released modifiers."""
        if isinstance(key, keyboard.Key):
            mod = _KEY_TO_MOD.get(key)
            if mod:
                self._active_mods.discard(mod)

    def register(self, hotkey: str, callback: Callable[[], None]) -> None:
        """Register a global hotkey. Unregisters the previous one first."""
        self.unregister()
        self._modifiers, self._trigger_vk = _parse_hotkey(hotkey)
        self._current_hotkey = hotkey
        self._callback = callback
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()
        log.info("Hotkey registered: %s", hotkey)

    def unregister(self) -> None:
        """Unregister the current hotkey, if any."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        self._current_hotkey = None
        self._callback = None
        self._trigger_vk = None
        self._modifiers = frozenset()
        self._active_mods.clear()

    @property
    def current_hotkey(self) -> str | None:
        """The currently registered hotkey string, or None."""
        return self._current_hotkey
