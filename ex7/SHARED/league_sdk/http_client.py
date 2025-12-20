"""
HTTP client with retry logic for MCP communication.

Implements exponential backoff for transient errors.
"""

import time
from dataclasses import dataclass
from typing import Any

import requests

from .models import MCPRequest, MCPResponse, MCPError


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = 3
    base_delay: float = 2.0
    backoff_multiplier: float = 2.0
    retryable_codes: tuple = ("E001", "E009")


class MCPClient:
    """HTTP client for MCP JSON-RPC 2.0 communication."""

    def __init__(self, retry_config: RetryConfig | None = None):
        """Initialize client with optional retry configuration."""
        self.retry_config = retry_config or RetryConfig()
        self._request_id = 0

    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self._request_id += 1
        return self._request_id

    def call(
        self,
        endpoint: str,
        method: str,
        params: dict[str, Any],
        timeout: int = 30,
    ) -> dict[str, Any]:
        """
        Send MCP request with retry logic.

        Args:
            endpoint: Target URL (e.g., "http://localhost:8000/mcp")
            method: JSON-RPC method name
            params: Method parameters (including envelope fields)
            timeout: Request timeout in seconds

        Returns:
            Response dictionary (result or error)
        """
        request = MCPRequest(
            method=method,
            params=params,
            id=self._next_request_id(),
        )

        last_error = None

        for attempt in range(self.retry_config.max_retries):
            try:
                response = requests.post(
                    endpoint,
                    json=request.model_dump(),
                    timeout=timeout,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                return response.json()

            except requests.Timeout as e:
                last_error = e
                if attempt < self.retry_config.max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)

            except requests.ConnectionError as e:
                last_error = e
                if attempt < self.retry_config.max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)

            except requests.HTTPError as e:
                # Don't retry HTTP errors (4xx, 5xx)
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": f"HTTP error: {e}",
                    },
                    "id": request.id,
                }

        # All retries exhausted
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32001,
                "message": f"Max retries exceeded: {last_error}",
                "data": {
                    "error_code": "E009",
                    "error_description": "CONNECTION_ERROR",
                },
            },
            "id": request.id,
        }

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for exponential backoff."""
        return self.retry_config.base_delay * (
            self.retry_config.backoff_multiplier ** attempt
        )

    def call_no_retry(
        self,
        endpoint: str,
        method: str,
        params: dict[str, Any],
        timeout: int = 30,
    ) -> dict[str, Any]:
        """
        Send MCP request without retry logic.

        Useful for time-sensitive operations where retry would cause issues.
        """
        request = MCPRequest(
            method=method,
            params=params,
            id=self._next_request_id(),
        )

        try:
            response = requests.post(
                endpoint,
                json=request.model_dump(),
                timeout=timeout,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()

        except requests.Timeout:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32001,
                    "message": "Request timeout",
                    "data": {
                        "error_code": "E001",
                        "error_description": "TIMEOUT_ERROR",
                    },
                },
                "id": request.id,
            }

        except requests.ConnectionError as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32001,
                    "message": f"Connection error: {e}",
                    "data": {
                        "error_code": "E009",
                        "error_description": "CONNECTION_ERROR",
                    },
                },
                "id": request.id,
            }

        except requests.HTTPError as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": f"HTTP error: {e}",
                },
                "id": request.id,
            }
