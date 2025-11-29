"""Configuration loader for Route Guide System."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class ConfigLoader:
    """Loads and manages configuration from YAML and environment variables."""

    def __init__(self, config_path: Optional[str] = None, env_path: Optional[str] = None):
        """
        Initialize the configuration loader.

        Args:
            config_path: Path to YAML config file (default: config/config.yaml)
            env_path: Path to .env file (default: .env in project root)
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.project_root / "config" / "config.yaml"
        self.env_path = env_path or self.project_root / ".env"

        # Load environment variables
        if self.env_path.exists():
            load_dotenv(self.env_path)

        # Load YAML configuration
        self.config = self._load_yaml_config()

    def _load_yaml_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Dictionary containing configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        if not Path(self.config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        return config or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Examples:
            config.get("api.google_maps.timeout")
            config.get("agents.video.weight", default=1.0)

        Args:
            key: Dot-notation key (e.g., "api.google_maps.timeout")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)

    def get_google_maps_api_key(self) -> str:
        """
        Get Google Maps API key from environment.

        Returns:
            API key

        Raises:
            ValueError: If API key not found
        """
        api_key = self.get_env("GOOGLE_MAPS_API_KEY")
        if not api_key or api_key == "your_google_maps_api_key_here":
            raise ValueError(
                "GOOGLE_MAPS_API_KEY not found in environment. "
                "Please copy .env.example to .env and set your API key."
            )
        return api_key

    def get_log_level(self) -> str:
        """
        Get log level from environment or config.

        Returns:
            Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Environment variable takes precedence
        env_level = self.get_env("LOG_LEVEL")
        if env_level:
            return env_level.upper()

        # Fall back to config file
        config_level = self.get("system.log_level", "INFO")
        return config_level.upper()

    def get_all_config(self) -> Dict[str, Any]:
        """
        Get complete configuration dictionary.

        Returns:
            Complete configuration
        """
        return self.config.copy()

    def reload(self) -> None:
        """Reload configuration from files."""
        if self.env_path.exists():
            load_dotenv(self.env_path, override=True)
        self.config = self._load_yaml_config()


# Global configuration instance
_config_instance: Optional[ConfigLoader] = None


def get_config() -> ConfigLoader:
    """
    Get global configuration instance (singleton pattern).

    Returns:
        ConfigLoader instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader()
    return _config_instance


def reload_config() -> None:
    """Reload global configuration."""
    global _config_instance
    if _config_instance is not None:
        _config_instance.reload()
