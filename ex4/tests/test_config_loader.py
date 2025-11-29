"""Unit tests for configuration loader."""

import os
import pytest
from pathlib import Path
from src.utils.config_loader import ConfigLoader


class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_load_config(self):
        """Test configuration loading."""
        config = ConfigLoader()
        assert config.config is not None
        assert isinstance(config.config, dict)

    def test_get_nested_value(self):
        """Test getting nested configuration value."""
        config = ConfigLoader()
        timeout = config.get("api.google_maps.timeout")
        assert timeout is not None
        assert isinstance(timeout, int)

    def test_get_with_default(self):
        """Test get with default value."""
        config = ConfigLoader()
        value = config.get("nonexistent.key", default=42)
        assert value == 42

    def test_get_env(self):
        """Test environment variable retrieval."""
        os.environ["TEST_VAR"] = "test_value"
        config = ConfigLoader()
        value = config.get_env("TEST_VAR")
        assert value == "test_value"
        del os.environ["TEST_VAR"]

    def test_get_env_with_default(self):
        """Test environment variable with default."""
        config = ConfigLoader()
        value = config.get_env("NONEXISTENT_VAR", default="default_value")
        assert value == "default_value"

    def test_get_log_level(self):
        """Test log level retrieval."""
        config = ConfigLoader()
        level = config.get_log_level()
        assert level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_get_all_config(self):
        """Test getting complete configuration."""
        config = ConfigLoader()
        all_config = config.get_all_config()
        assert isinstance(all_config, dict)
        assert "api" in all_config
        assert "agents" in all_config
