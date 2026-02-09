"""
Settings Management
Handles application configuration and persistence.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """Manages application settings with persistence."""

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            self.config_dir = Path(__file__).parent.parent.parent / "data"
        else:
            self.config_dir = Path(config_dir)

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self._load()

    def _load(self):
        """Load settings from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                self.config = self._default_config()
        else:
            self.config = self._default_config()

    def _save(self):
        """Save settings to disk."""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "llm": {
                "provider": "ollama",
                "model": "qwen2.5:14b",
                "api_key": None
            },
            "ocr": {
                "language": "eng"
            },
            "capture": {
                "auto_delay": 1.5,
                "default_app": "kindle"
            },
            "embedding": {
                "model": "all-MiniLM-L6-v2",
                "chunk_size": 1000,
                "chunk_overlap": 200
            }
        }

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.config.get("llm", self._default_config()["llm"])

    def save_llm_config(
        self,
        provider: str,
        model: str,
        api_key: Optional[str] = None
    ):
        """
        Save LLM configuration.

        Args:
            provider: LLM provider name
            model: Model name
            api_key: Optional API key
        """
        self.config["llm"] = {
            "provider": provider,
            "model": model,
            "api_key": api_key
        }
        self._save()

    def get_ocr_config(self) -> Dict[str, Any]:
        """Get OCR configuration."""
        return self.config.get("ocr", self._default_config()["ocr"])

    def save_ocr_config(self, language: str):
        """
        Save OCR configuration.

        Args:
            language: OCR language code
        """
        self.config["ocr"] = {"language": language}
        self._save()

    def get_capture_config(self) -> Dict[str, Any]:
        """Get capture configuration."""
        return self.config.get("capture", self._default_config()["capture"])

    def save_capture_config(self, auto_delay: float, default_app: str):
        """
        Save capture configuration.

        Args:
            auto_delay: Delay between auto captures
            default_app: Default ebook app
        """
        self.config["capture"] = {
            "auto_delay": auto_delay,
            "default_app": default_app
        }
        self._save()

    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration."""
        return self.config.get("embedding", self._default_config()["embedding"])

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key (dot notation supported, e.g., "llm.provider")
            default: Default value if not found

        Returns:
            Setting value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set a setting value.

        Args:
            key: Setting key (dot notation supported)
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        self._save()

    def reset(self):
        """Reset all settings to defaults."""
        self.config = self._default_config()
        self._save()
