"""Ollama API client for interacting with local LLM models."""

import requests
from typing import List, Dict, Optional


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama client.
        
        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 30
    
    def check_connection(self) -> bool:
        """Check if Ollama service is running.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return False
    
    def list_models(self) -> List[str]:
        """List available Ollama models.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except (requests.exceptions.RequestException, KeyError):
            return []
    
    def send_message(
        self,
        model: str,
        message: str,
        history: Optional[List[Dict]] = None
    ) -> str:
        """Send a message to the model and get response.
        
        Args:
            model: Model name to use
            message: User message
            history: Optional conversation history (list of messages with 'role' and 'content')
            
        Returns:
            Model response text
        """
        # Build messages list for chat API
        messages = []
        if history:
            messages = history.copy()
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract response from chat API format
            assistant_message = data.get('message', {})
            if isinstance(assistant_message, dict):
                return assistant_message.get('content', '')
            return str(assistant_message) if assistant_message else ''
        except requests.exceptions.Timeout:
            raise ConnectionError("Request timed out. The model may be taking too long to respond.")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get response: {e}")

