# Retext

## What is this?
System-wide Windows 11 text rewriter. Select text anywhere, press hotkey, get grammar/casing/punctuation corrected in place. Auto-detects language. Powered by Gemini.

## Tech Stack
- Python 3.12+
- `pynput` for global hotkeys + key simulation
- `pyperclip` for clipboard read/write
- `google-genai` for Gemini API
- `pystray` + `Pillow` for system tray
- `tkinter` for settings UI
- Config: JSON in `%APPDATA%/Retext/`

## Directory Structure
```
src/rewrite/          — Main package
  main.py             — Entry point: tray + hotkey + pipeline
  hotkey.py           — Global hotkey listener (pynput)
  clipboard.py        — Save/capture/replace/restore clipboard
  rewriter.py         — System prompt + post-processing
  config.py           — JSON config load/save
  settings.py         — tkinter settings window
  providers/
    base.py           — Abstract provider interface
    gemini.py         — Google Gemini provider
tests/                — pytest tests
scripts/build.bat     — PyInstaller build script
assets/icon.ico       — Tray icon
```

## Commands
- `python -m rewrite.main` — Run the app (with PYTHONPATH=src)
- `pytest` — Run tests
- `ruff check src/` — Lint
- `ruff format src/` — Format

## Key Design Decisions
- Gemini-only for now (simplicity over flexibility)
- Clipboard pipeline: save → release modifiers → Ctrl+C → send to AI → Ctrl+V → restore
- Hotkey matching uses Windows VK codes to handle modifier combos correctly
- 500ms debounce prevents multiple triggers from key repeat
- Config stored in `%APPDATA%/Retext/config.json`
