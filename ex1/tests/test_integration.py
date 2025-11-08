"""Integration tests for the chat application."""

import pytest
from src.api.ollama_client import OllamaClient


def test_end_to_end_chat_flow():
    """Test complete chat flow from connection to message exchange.
    
    Expected: 
    - Connection check returns True
    - Models can be listed
    - Messages can be sent and responses received
    """
    client = OllamaClient()
    
    # Check connection
    if not client.check_connection():
        pytest.skip("Ollama is not running")
    
    # List models
    models = client.list_models()
    if not models:
        pytest.skip("No models available")
    
    # Send message
    model = models[0]
    response = client.send_message(model, "Say hello in one word")
    assert isinstance(response, str)
    assert len(response) > 0


def test_model_switching():
    """Test switching between different models.
    
    Expected: Different models can be used to send messages.
    """
    client = OllamaClient()
    
    if not client.check_connection():
        pytest.skip("Ollama is not running")
    
    models = client.list_models()
    if len(models) < 2:
        pytest.skip("Need at least 2 models for this test")
    
    # Test first model
    response1 = client.send_message(models[0], "Hello")
    assert isinstance(response1, str)
    
    # Test second model
    response2 = client.send_message(models[1], "Hello")
    assert isinstance(response2, str)


def test_error_handling():
    """Test error handling for invalid requests.
    
    Expected: Appropriate errors raised for invalid model names.
    """
    client = OllamaClient()
    
    if not client.check_connection():
        pytest.skip("Ollama is not running")
    
    # Test with invalid model name
    with pytest.raises((ConnectionError, Exception)):
        client.send_message("nonexistent_model_12345", "Hello")

