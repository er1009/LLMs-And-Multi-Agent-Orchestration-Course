"""Info Agent implementation for Route Guide System."""

import json
import re
from pathlib import Path
from typing import Dict

from .base_agent import BaseAgent, AgentResult
from ..utils.logger import get_logger

logger = get_logger(__name__)


class InfoAgent(BaseAgent):
    """
    Agent for finding historical and factual information about a location.

    Uses Claude to provide educational content, fun facts, and stories.
    Prompt is loaded from prompts/info_agent.md
    """

    def __init__(self, claude_client, timeout: int = 30):
        """
        Initialize Info Agent.

        Args:
            claude_client: Claude CLI client
            timeout: Execution timeout
        """
        super().__init__(claude_client, "info", timeout)
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load prompt template from markdown file."""
        prompt_path = Path(__file__).parent / "prompts" / "info_agent.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _create_prompt(self, address: str, context: Dict) -> str:
        """
        Create prompt for finding information.

        Args:
            address: Location address
            context: Additional context

        Returns:
            Prompt string
        """
        # Substitute address in template
        prompt = self.prompt_template.replace("{{ADDRESS}}", address)
        return prompt

    def _parse_response(self, response: str, address: str) -> AgentResult:
        """
        Parse Claude's response into AgentResult.

        Args:
            response: Claude's JSON response
            address: Original address

        Returns:
            AgentResult with information

        Raises:
            ValueError: If response parsing fails
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")

            data = json.loads(json_match.group())

            # Validate required fields
            required_fields = ["title", "summary"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Combine summary and highlights into content
            content = data["summary"]
            if data.get("highlights"):
                content += "\n\nKey Facts:\n" + "\n".join(
                    f"• {highlight}" for highlight in data["highlights"]
                )

            # Create result
            return AgentResult(
                agent_type=self.agent_type,
                title=data["title"],
                content=content,
                metadata={
                    "address": address,
                    "summary": data["summary"],
                    "highlights": data.get("highlights", []),
                    "reference_url": data.get("reference_url", ""),
                    "category": data.get("category", "General"),
                    "source": "information"
                },
                success=True
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse info agent response: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid response format: {e}")
