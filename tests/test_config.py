import json

from rewrite.config import DEFAULT_CONFIG, load_config, save_config


def test_default_config_returned_when_no_file(temp_config_dir):
    config = load_config()
    assert config == DEFAULT_CONFIG


def test_save_and_load_roundtrip(temp_config_dir, sample_config):
    save_config(sample_config)
    loaded = load_config()
    assert loaded == sample_config


def test_missing_keys_filled_with_defaults(temp_config_dir):
    """If config file has fewer keys than defaults, missing keys get default values."""
    partial = {"gemini_api_key": "my-key"}
    save_config(partial)
    loaded = load_config()
    assert loaded["gemini_api_key"] == "my-key"
    assert loaded["hotkey"] == DEFAULT_CONFIG["hotkey"]
    assert loaded["gemini_model"] == DEFAULT_CONFIG["gemini_model"]


def test_config_dir_created(tmp_path):
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {"APPDATA": str(tmp_path / "subdir")}):
        from rewrite import config

        result = config.get_config_dir()
        assert result.exists()


def test_save_creates_file(temp_config_dir, sample_config):
    save_config(sample_config)
    config_file = temp_config_dir / "config.json"
    assert config_file.exists()
    data = json.loads(config_file.read_text())
    assert data["gemini_api_key"] == "test-gemini-key"
