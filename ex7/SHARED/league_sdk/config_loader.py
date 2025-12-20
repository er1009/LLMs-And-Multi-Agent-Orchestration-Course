"""
Configuration loading utilities.

Loads JSON configuration files from the SHARED/config directory.
"""

import json
from pathlib import Path
from typing import Any


class ConfigLoader:
    """Loader for JSON configuration files."""

    def __init__(self, config_root: Path | str = "SHARED/config"):
        """
        Initialize config loader.

        Args:
            config_root: Root directory for configuration files
        """
        self.config_root = Path(config_root)

    def load(self, config_path: str) -> dict[str, Any]:
        """
        Load a JSON configuration file.

        Args:
            config_path: Relative path from config root (e.g., "system.json")

        Returns:
            Parsed JSON as dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        full_path = self.config_root / config_path
        with full_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def load_system(self) -> dict[str, Any]:
        """Load system configuration."""
        return self.load("system.json")

    def load_agents(self) -> dict[str, Any]:
        """Load agents configuration."""
        return self.load("agents/agents_config.json")

    def load_league(self, league_id: str) -> dict[str, Any]:
        """Load league configuration."""
        return self.load(f"leagues/{league_id}.json")

    def load_games(self) -> dict[str, Any]:
        """Load games registry."""
        return self.load("games/games_registry.json")

    def save(self, config_path: str, data: dict[str, Any]) -> None:
        """
        Save data to a JSON configuration file.

        Args:
            config_path: Relative path from config root
            data: Data to save
        """
        full_path = self.config_root / config_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with full_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class DataLoader:
    """Loader for runtime data files (standings, matches, etc.)."""

    def __init__(self, data_root: Path | str = "SHARED/data"):
        """
        Initialize data loader.

        Args:
            data_root: Root directory for data files
        """
        self.data_root = Path(data_root)

    def load(self, data_path: str) -> dict[str, Any]:
        """
        Load a JSON data file.

        Args:
            data_path: Relative path from data root

        Returns:
            Parsed JSON as dictionary, or empty dict if file doesn't exist
        """
        full_path = self.data_root / data_path
        if not full_path.exists():
            return {}
        with full_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data_path: str, data: dict[str, Any]) -> None:
        """
        Save data to a JSON file.

        Args:
            data_path: Relative path from data root
            data: Data to save
        """
        full_path = self.data_root / data_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with full_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_standings(self, league_id: str) -> dict[str, Any]:
        """Load league standings."""
        return self.load(f"leagues/{league_id}/standings.json")

    def save_standings(self, league_id: str, standings: dict[str, Any]) -> None:
        """Save league standings."""
        self.save(f"leagues/{league_id}/standings.json", standings)

    def load_match(self, league_id: str, match_id: str) -> dict[str, Any]:
        """Load match data."""
        return self.load(f"matches/{league_id}/{match_id}.json")

    def save_match(
        self,
        league_id: str,
        match_id: str,
        data: dict[str, Any],
    ) -> None:
        """Save match data."""
        self.save(f"matches/{league_id}/{match_id}.json", data)
