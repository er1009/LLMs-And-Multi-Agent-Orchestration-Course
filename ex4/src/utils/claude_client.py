"""Claude CLI client wrapper for Route Guide System."""

import json
import subprocess
import time
from typing import Any, Dict, Optional

from .logger import get_logger

logger = get_logger(__name__)


class ClaudeClientError(Exception):
    """Exception raised for Claude CLI errors."""
    pass


class ClaudeClient:
    """
    Wrapper for calling Claude via CLI.

    Handles subprocess invocation, error handling, and response parsing.
    """

    def __init__(
        self,
        cli_command: str = "claude",
        timeout: int = 30,
        max_retries: int = 2,
        retry_delay: int = 2
    ):
        """
        Initialize Claude CLI client.

        Args:
            cli_command: Command to invoke Claude CLI
            timeout: Timeout for Claude invocation (seconds)
            max_retries: Maximum retry attempts for transient errors
            retry_delay: Delay between retries (seconds)
        """
        self.cli_command = cli_command
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call Claude with a prompt via CLI.

        Args:
            prompt: User prompt to send to Claude
            system_prompt: Optional system prompt

        Returns:
            Claude's response text

        Raises:
            ClaudeClientError: If Claude invocation fails
        """
        for attempt in range(self.max_retries + 1):
            try:
                return self._invoke_claude(prompt, system_prompt)
            except subprocess.TimeoutExpired:
                if attempt < self.max_retries:
                    logger.warning(
                        f"Claude CLI timeout (attempt {attempt + 1}/{self.max_retries + 1}), retrying..."
                    )
                    time.sleep(self.retry_delay)
                else:
                    raise ClaudeClientError(
                        f"Claude CLI timed out after {self.max_retries + 1} attempts"
                    )
            except subprocess.CalledProcessError as e:
                if attempt < self.max_retries and self._is_transient_error(e):
                    logger.warning(
                        f"Claude CLI error (attempt {attempt + 1}/{self.max_retries + 1}), retrying..."
                    )
                    time.sleep(self.retry_delay)
                else:
                    raise ClaudeClientError(
                        f"Claude CLI failed with exit code {e.returncode}: {e.stderr}"
                    )
            except Exception as e:
                raise ClaudeClientError(f"Unexpected error calling Claude: {str(e)}")

        raise ClaudeClientError("Failed to invoke Claude after all retry attempts")

    def _invoke_claude(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Invoke Claude CLI subprocess.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Claude's response

        Raises:
            subprocess.TimeoutExpired: If call times out
            subprocess.CalledProcessError: If call fails
        """
        # Construct command
        # Using echo to pipe prompt to claude
        cmd = f'echo {self._escape_prompt(prompt)} | {self.cli_command}'

        if system_prompt:
            # Note: Claude CLI syntax may vary - adjust as needed
            cmd = f'echo {self._escape_prompt(prompt)} | {self.cli_command} --system {self._escape_prompt(system_prompt)}'

        logger.debug(f"Invoking Claude CLI: {self.cli_command}")

        # Execute command
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            check=True
        )

        response = result.stdout.strip()

        if not response:
            raise ClaudeClientError("Claude returned empty response")

        logger.debug(f"Claude response length: {len(response)} characters")

        return response

    def _escape_prompt(self, prompt: str) -> str:
        """
        Escape prompt for shell command.

        Args:
            prompt: Prompt to escape

        Returns:
            Escaped prompt
        """
        # Use single quotes and escape any single quotes in the prompt
        escaped = prompt.replace("'", "'\\''")
        return f"'{escaped}'"

    def _is_transient_error(self, error: subprocess.CalledProcessError) -> bool:
        """
        Determine if error is transient (retriable).

        Args:
            error: Subprocess error

        Returns:
            True if error appears transient
        """
        # Check stderr for common transient error patterns
        stderr = error.stderr.lower() if error.stderr else ""

        transient_patterns = [
            "network",
            "connection",
            "timeout",
            "temporary",
            "rate limit",
            "throttle"
        ]

        return any(pattern in stderr for pattern in transient_patterns)

    def call_with_json_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call Claude and parse JSON response.

        Args:
            prompt: User prompt (should request JSON format)
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON response

        Raises:
            ClaudeClientError: If invocation or parsing fails
        """
        response = self.call(prompt, system_prompt)

        try:
            # Try to find JSON in response (Claude might add explanation text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON object found in response")

            json_str = response[json_start:json_end]
            return json.loads(json_str)

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON from Claude response: {e}")
            logger.debug(f"Response was: {response}")
            raise ClaudeClientError(f"Failed to parse JSON response: {e}")

    def check_availability(self) -> bool:
        """
        Check if Claude CLI is available.

        Returns:
            True if Claude CLI is accessible
        """
        try:
            result = subprocess.run(
                [self.cli_command, "--version"],
                capture_output=True,
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
