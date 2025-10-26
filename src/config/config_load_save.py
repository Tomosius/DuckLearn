from pathlib import Path

import orjson
from platformdirs import user_config_dir


class ConfigManager:
    """Handles only loading and saving JSON configuration."""

    def __init__(
        self, app_name: str = 'DuckLearn', filename: str = 'settings.json'
    ):
        """Initialize configuration paths and load existing data if available."""
        self.app_name: str = app_name
        self.filename: str = filename
        self._config_dir: Path = Path(user_config_dir(self.app_name))
        self._config_path: Path = self._config_dir / self.filename
        self.data: dict = {}

        self._config_dir.mkdir(parents=True, exist_ok=True)
        self.data = self.load()

    def load(self) -> dict:
        """Load settings from JSON file, or return empty dict if not found."""
        config_path: Path = self._config_path
        if config_path.exists():
            try:
                return orjson.loads(config_path.read_bytes())
            except (OSError, orjson.JSONDecodeError):
                print('⚠️ Failed to load config. Returning empty config.')
                return {}
        else:
            self.save({})
            return {}

    def save(self, data: dict | None = None) -> None:
        """Save provided data (or current self.data) to JSON."""
        payload: dict = data if data is not None else self.data
        json_bytes: bytes = orjson.dumps(
            payload,
            option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS,
        )
        self._config_path.write_bytes(json_bytes)

    @property
    def path(self) -> Path:
        """Return the config file path."""
        return self._config_path


# --- Global instance (optional) ---
Config: ConfigManager = ConfigManager()
