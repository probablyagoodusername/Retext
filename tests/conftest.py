from unittest.mock import patch

import pytest


@pytest.fixture
def temp_config_dir(tmp_path):
    """Provide a temp directory for config files."""
    with patch("rewrite.config.get_config_dir", return_value=tmp_path):
        yield tmp_path


@pytest.fixture
def sample_config():
    """Return a sample config dict."""
    return {
        "hotkey": "ctrl+shift+r",
        "gemini_api_key": "test-gemini-key",
        "gemini_model": "gemini-2.5-flash",
    }
