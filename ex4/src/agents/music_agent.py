"""Music Agent implementation for Route Guide System."""

import json
import re
from pathlib import Path
from typing import Dict

from .base_agent import BaseAgent, AgentResult
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MusicAgent(BaseAgent):
    """
    Agent for finding relevant music for a location.

    Uses Claude to recommend contextually appropriate music from YouTube or Spotify.
    Prompt is loaded from prompts/music_agent.md
    """

    def __init__(self, claude_client, timeout: int = 30):
        """
        Initialize Music Agent.

        Args:
            claude_client: Claude CLI client
            timeout: Execution timeout
        """
        super().__init__(claude_client, "music", timeout)
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load prompt template from markdown file."""
        prompt_path = Path(__file__).parent / "prompts" / "music_agent.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _create_prompt(self, address: str, context: Dict) -> str:
        """
        Create prompt for finding relevant music.

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
            AgentResult with music recommendation

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
            required_fields = ["title", "artist", "url"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Create result
            return AgentResult(
                agent_type=self.agent_type,
                title=f"{data['title']} - {data['artist']}",
                content=data["url"],
                metadata={
                    "address": address,
                    "artist": data["artist"],
                    "genre": data.get("genre", "Unknown"),
                    "relevance_reason": data.get("relevance_reason", ""),
                    "mood": data.get("mood", ""),
                    "source": "youtube" if "youtube.com" in data["url"].lower() else "spotify"
                },
                success=True
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse music agent response: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid response format: {e}")
