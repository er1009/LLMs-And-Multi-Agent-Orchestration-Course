"""
JSON structured logging for the league system.

Logs are written in JSON-lines format for easy parsing and analysis.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JsonLogger:
    """JSON-lines structured logger."""

    LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")

    def __init__(
        self,
        component: str,
        league_id: str | None = None,
        log_root: Path | str = "SHARED/logs",
    ):
        """
        Initialize logger for a component.

        Args:
            component: Component name (e.g., "league_manager", "REF01", "P01")
            league_id: Optional league ID for league-specific logs
            log_root: Root directory for logs
        """
        self.component = component
        log_root = Path(log_root)

        if league_id:
            subdir = log_root / "league" / league_id
        else:
            subdir = log_root / "agents"

        subdir.mkdir(parents=True, exist_ok=True)
        self.log_file = subdir / f"{component}.log.jsonl"

    def _write(self, entry: dict[str, Any]) -> None:
        """Write log entry to file."""
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

    def log(
        self,
        event_type: str,
        level: str = "INFO",
        **details: Any,
    ) -> None:
        """
        Write a structured log entry.

        Args:
            event_type: Type of event (e.g., "REGISTRATION", "GAME_START")
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            **details: Additional key-value pairs to include
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "component": self.component,
            "event_type": event_type,
            "level": level,
            **details,
        }
        self._write(entry)

        # Also print to console for debugging
        print(f"[{level}] {self.component}: {event_type} - {details}")

    def debug(self, event_type: str, **details: Any) -> None:
        """Log at DEBUG level."""
        self.log(event_type, level="DEBUG", **details)

    def info(self, event_type: str, **details: Any) -> None:
        """Log at INFO level."""
        self.log(event_type, level="INFO", **details)

    def warning(self, event_type: str, **details: Any) -> None:
        """Log at WARNING level."""
        self.log(event_type, level="WARNING", **details)

    def error(self, event_type: str, **details: Any) -> None:
        """Log at ERROR level."""
        self.log(event_type, level="ERROR", **details)

    def log_message(
        self,
        direction: str,
        message_type: str,
        endpoint: str | None = None,
        **details: Any,
    ) -> None:
        """
        Log an MCP message.

        Args:
            direction: "SENT" or "RECEIVED"
            message_type: MCP message type
            endpoint: Target/source endpoint
            **details: Additional message details
        """
        self.info(
            f"MCP_{direction}",
            message_type=message_type,
            endpoint=endpoint,
            **details,
        )
