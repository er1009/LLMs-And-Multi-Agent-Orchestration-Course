"""Video Agent implementation for Route Guide System."""

import json
import re
from pathlib import Path
from typing import Dict

from .base_agent import BaseAgent, AgentResult
from ..utils.logger import get_logger

logger = get_logger(__name__)


class VideoAgent(BaseAgent):
    """
    Agent for finding relevant YouTube videos for a location.

    Uses Claude to recommend contextually relevant videos.
    Prompt is loaded from prompts/video_agent.md
    """

    def __init__(self, claude_client, timeout: int = 30):
        """
        Initialize Video Agent.

        Args:
            claude_client: Claude CLI client
            timeout: Execution timeout
        """
        super().__init__(claude_client, "video", timeout)
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load prompt template from markdown file."""
        prompt_path = Path(__file__).parent / "prompts" / "video_agent.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _create_prompt(self, address: str, context: Dict) -> str:
        """
        Create prompt for finding a relevant video.

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
            AgentResult with video recommendation

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
            required_fields = ["title", "url", "description"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Create result
            return AgentResult(
                agent_type=self.agent_type,
                title=data["title"],
                content=data["url"],
                metadata={
                    "address": address,
                    "description": data["description"],
                    "channel": data.get("channel", "Unknown"),
                    "relevance_reason": data.get("relevance_reason", ""),
                    "source": "youtube"
                },
                success=True
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse video agent response: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid response format: {e}")
