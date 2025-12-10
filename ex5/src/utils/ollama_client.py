"""Ollama API client with robust error handling and retry logic.

This module provides a reliable interface to the Ollama API with:
- Automatic retries with exponential backoff
- Connection health checks
- Timeout handling
- Comprehensive error messages
"""

import time
import logging
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from src.config.settings import config

logger = logging.getLogger(__name__)


class OllamaConnectionError(Exception):
    """Raised when Ollama service is unreachable."""
    pass


class OllamaTimeoutError(Exception):
    """Raised when Ollama request times out."""
    pass


class OllamaClient:
    """Client for interacting with Ollama API.

    Provides robust querying with automatic retries, timeouts,
    and connection validation.

    Attributes:
        base_url: Ollama API base URL
        default_model: Default model to use
        default_temperature: Default sampling temperature
        timeout: Default timeout in seconds
        max_retries: Maximum retry attempts
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3
    ):
        """Initialize Ollama client.

        Args:
            base_url: Ollama API URL (default from config)
            model: Model name (default from config)
            temperature: Sampling temperature (default from config)
            timeout: Request timeout in seconds (default from config)
            max_retries: Maximum retry attempts on failure
        """
        self.base_url = base_url or config.ollama_base_url
        self.default_model = model or config.ollama_model
        self.default_temperature = temperature or config.ollama_temperature
        self.timeout = timeout or config.ollama_timeout
        self.max_retries = max_retries

        # Validate connection on initialization
        self.check_connection()

    def check_connection(self) -> bool:
        """Check if Ollama service is reachable.

        Returns:
            True if connection successful

        Raises:
            OllamaConnectionError: If Ollama is unreachable
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Successfully connected to Ollama at {self.base_url}")
            return True
        except RequestException as e:
            error_msg = (
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Please ensure Ollama is running (ollama serve). "
                f"Error: {e}"
            )
            logger.error(error_msg)
            raise OllamaConnectionError(error_msg)

    def get_available_models(self) -> list:
        """Get list of available models.

        Returns:
            List of model names
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            models = [model["name"] for model in response.json().get("models", [])]
            logger.debug(f"Available models: {models}")
            return models
        except RequestException as e:
            logger.warning(f"Could not fetch available models: {e}")
            return []

    def query(
        self,
        context: str,
        question: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> str:
        """Send query to Ollama and return response.

        Automatically retries with exponential backoff on transient failures.

        Args:
            context: Background context for the question
            question: The question to answer
            model: Model name (uses default if not specified)
            temperature: Sampling temperature (uses default if not specified)
            max_tokens: Maximum tokens in response
            timeout: Request timeout (uses default if not specified)

        Returns:
            Model response as string

        Raises:
            OllamaConnectionError: If Ollama is unreachable
            OllamaTimeoutError: If request times out
            RuntimeError: If max retries exceeded
        """
        model = model or self.default_model
        temperature = temperature or self.default_temperature
        timeout = timeout or self.timeout

        # Construct prompt
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Sending query to Ollama (attempt {attempt + 1}/{self.max_retries})"
                )

                start_time = time.perf_counter()

                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    }
                }

                if max_tokens:
                    payload["options"]["num_predict"] = max_tokens

                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=timeout
                )

                response.raise_for_status()

                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Query completed in {elapsed_ms:.2f}ms")

                result = response.json()["response"]
                return result.strip()

            except Timeout:
                if attempt == self.max_retries - 1:
                    raise OllamaTimeoutError(
                        f"Request timed out after {timeout}s and {self.max_retries} attempts"
                    )
                logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff

            except ConnectionError:
                if attempt == self.max_retries - 1:
                    raise OllamaConnectionError(
                        f"Cannot connect to Ollama after {self.max_retries} attempts"
                    )
                logger.warning(f"Connection error on attempt {attempt + 1}, retrying...")
                time.sleep(2 ** attempt)

            except RequestException as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"Ollama request failed after {self.max_retries} attempts: {e}"
                    )
                logger.warning(f"Request error on attempt {attempt + 1}: {e}, retrying...")
                time.sleep(2 ** attempt)

        # Should never reach here due to raises above, but for safety
        raise RuntimeError("Query failed after all retries")

    def query_with_timing(
        self,
        context: str,
        question: str,
        **kwargs
    ) -> tuple[str, float]:
        """Query Ollama and return response with latency measurement.

        Args:
            context: Background context
            question: Question to answer
            **kwargs: Additional arguments passed to query()

        Returns:
            Tuple of (response, latency_ms)
        """
        start_time = time.perf_counter()
        response = self.query(context, question, **kwargs)
        latency_ms = (time.perf_counter() - start_time) * 1000

        return response, latency_ms

    def warmup(self) -> None:
        """Perform warmup query to initialize model.

        Useful before starting timed experiments to exclude
        model loading time from measurements.
        """
        logger.info("Warming up Ollama model...")
        try:
            self.query(
                context="This is a warmup query.",
                question="What is 2+2?",
                timeout=30
            )
            logger.info("Warmup completed successfully")
        except Exception as e:
            logger.warning(f"Warmup failed (this may be okay): {e}")
