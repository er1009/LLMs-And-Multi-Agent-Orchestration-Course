"""
League SDK - Shared utilities for the AI Agent League System.

This package provides common functionality used by all agents:
- Pydantic models for MCP messages
- HTTP client with retry logic
- JSON structured logging
- Configuration loading
"""

from .models import (
    MCPRequest,
    MCPResponse,
    MCPError,
    MessageType,
    GameResult,
    PlayerStanding,
    MatchInfo,
)
from .http_client import MCPClient, RetryConfig
from .logger import JsonLogger
from .config_loader import ConfigLoader

__all__ = [
    "MCPRequest",
    "MCPResponse",
    "MCPError",
    "MessageType",
    "GameResult",
    "PlayerStanding",
    "MatchInfo",
    "MCPClient",
    "RetryConfig",
    "JsonLogger",
    "ConfigLoader",
]

__version__ = "1.0.0"
