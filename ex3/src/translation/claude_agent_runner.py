"""
Claude CLI Agent Runner

Executes translation agents defined in MD files via Claude CLI.
"""

import subprocess
import json
from pathlib import Path
from typing import Optional


class ClaudeAgentRunner:
    """
    Runner for executing Claude CLI agents.

    Translates text by passing it to agent MD files via Claude CLI.
    """

    def __init__(self, agent_file: str):
        """
        Initialize the agent runner.

        Args:
            agent_file: Path to agent MD file
        """
        self.agent_file = Path(agent_file)
        if not self.agent_file.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_file}")

    def run(self, text: str, timeout: int = 60) -> str:
        """
        Run the agent on the given text.

        Args:
            text: Text to process
            timeout: Timeout in seconds (default: 60)

        Returns:
            Agent output (translated text)

        Raises:
            ValueError: If text is empty
            RuntimeError: If agent execution fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            # Prepare prompt combining agent instructions and text
            with open(self.agent_file, "r", encoding="utf-8") as f:
                agent_prompt = f.read()

            full_prompt = f"{agent_prompt}\n\n## Text to Translate:\n{text}"

            # Execute via Claude CLI
            # Note: This assumes Claude CLI is available and configured
            # Adjust command based on actual Claude CLI interface
            result = subprocess.run(
                ["claude", "--prompt", full_prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Agent execution failed: {result.stderr}")

            output = result.stdout.strip()
            return output

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Agent execution timed out after {timeout} seconds")
        except Exception as e:
            raise RuntimeError(f"Agent execution failed: {str(e)}") from e


def run_translation_pipeline(
    text: str,
    agent_files: list[str],
    timeout: int = 60,
) -> list[str]:
    """
    Run a translation pipeline through multiple agents.

    Args:
        text: Initial text to translate
        agent_files: List of agent MD file paths in execution order
        timeout: Timeout per agent in seconds

    Returns:
        List of translations (one per agent)

    Raises:
        ValueError: If inputs are invalid
        RuntimeError: If pipeline execution fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if not agent_files:
        raise ValueError("Agent files list cannot be empty")

    translations = []
    current_text = text

    for agent_file in agent_files:
        runner = ClaudeAgentRunner(agent_file)
        current_text = runner.run(current_text, timeout=timeout)
        translations.append(current_text)

    return translations
