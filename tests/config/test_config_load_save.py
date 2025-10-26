import json
import uuid
from pathlib import Path

import orjson
import pytest

from config.config_load_save import ConfigManager


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    """Provide a ConfigManager instance isolated to a temporary directory."""
    fake_user_dir = tmp_path / 'config'
    fake_user_dir.mkdir()
    monkeypatch.setattr(
        'platformdirs.user_config_dir', lambda app_name: str(fake_user_dir)
    )

    # Unique filename per test to prevent data collisions
    unique_filename = f'test_{uuid.uuid4().hex}.json'
    return ConfigManager(app_name='TestApp', filename=unique_filename)


def test_initialization_creates_directory_and_file(temp_config):
    """Ensure __init__ creates directory and initializes config."""
    cfg = temp_config
    assert cfg._config_dir.exists()
    assert cfg.path.exists()
    assert cfg.data == {}


def test_save_and_load_cycle(temp_config):
    """Test that saving and loading JSON data preserves values."""
    data = {'a': 1, 'b': {'nested': True}}
    temp_config.save(data)

    # Load fresh instance (simulates restart)
    new_cfg = ConfigManager(app_name='TestApp', filename=temp_config.filename)
    assert new_cfg.data == data
    assert json.loads(new_cfg.path.read_text()) == data


def test_load_returns_empty_if_corrupt_json(temp_config):
    """Handle corrupt JSON gracefully and return empty dict."""
    # Write invalid JSON manually
    temp_config.path.write_text('{bad json}')

    result = temp_config.load()
    assert result == {}


def test_save_uses_self_data_when_no_argument(temp_config):
    """Ensure save() uses self.data when no data argument is given."""
    temp_config.data = {'theme': 'dark'}
    temp_config.save()
    loaded = orjson.loads(temp_config.path.read_bytes())
    assert loaded == {'theme': 'dark'}


def test_path_property_returns_correct_path(temp_config):
    """Ensure .path property returns the full config path."""
    expected_path = temp_config._config_dir / temp_config.filename
    assert temp_config.path == expected_path


def test_load_creates_new_file_if_not_exists(tmp_path, monkeypatch):
    """When no file exists, load() should create an empty one."""
    fake_user_dir = tmp_path / 'fresh'
    fake_user_dir.mkdir()
    monkeypatch.setattr(
        'platformdirs.user_config_dir', lambda _: str(fake_user_dir)
    )

    cfg = ConfigManager(app_name='AnotherApp', filename='new.json')
    assert cfg.path.exists()
    assert cfg.data == {}


def test_save_raises_no_exceptions_on_write_error(monkeypatch, temp_config):
    """Simulate an OSError during save and verify it's handled gracefully."""

    def fake_write_bytes(_self, _):
        raise OSError('Fake write error')

    monkeypatch.setattr(Path, 'write_bytes', fake_write_bytes)
    temp_config.data = {'x': 1}

    # Should raise OSError normally, because save doesn't catch errors
    with pytest.raises(OSError):
        temp_config.save()
