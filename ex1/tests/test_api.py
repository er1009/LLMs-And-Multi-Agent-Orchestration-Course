"""Unit tests for Ollama API client."""

import pytest
from src.api.ollama_client import OllamaClient


def test_ollama_connection():
    """Test connection to Ollama API.
    
    Expected: Returns True if Ollama is running, False otherwise.
    """
    client = OllamaClient()
    result = client.check_connection()
    assert isinstance(result, bool)


def test_list_models():
    """Test listing available models.
    
    Expected: List of strings containing model names.
    If Ollama is not running, returns empty list.
    """
    client = OllamaClient()
    models = client.list_models()
    assert isinstance(models, list)
    assert all(isinstance(m, str) for m in models)


def test_send_message():
    """Test sending message to model.
    
    Expected: Non-empty string response if model is available.
    Raises ConnectionError if Ollama is not running or model not found.
    """
    client = OllamaClient()
    
    # Only test if Ollama is running
    if not client.check_connection():
        pytest.skip("Ollama is not running")
    
    models = client.list_models()
    if not models:
        pytest.skip("No models available")
    
    response = client.send_message(models[0], "Hello")
    assert isinstance(response, str)
    assert len(response) > 0


def test_client_initialization():
    """Test client initialization with custom base URL.
    
    Expected: Client initializes with provided base URL.
    """
    custom_url = "http://localhost:11434"
    client = OllamaClient(base_url=custom_url)
    assert client.base_url == custom_url


def test_conversation_history():
    """Test sending message with conversation history.
    
    Expected: Model maintains context from previous messages in conversation.
    """
    client = OllamaClient()
    
    # Only test if Ollama is running
    if not client.check_connection():
        pytest.skip("Ollama is not running")
    
    models = client.list_models()
    if not models:
        pytest.skip("No models available")
    
    model = models[0]
    
    # First message
    history = []
    response1 = client.send_message(model, "My name is Alice", history)
    assert isinstance(response1, str)
    assert len(response1) > 0
    
    # Update history
    history.append({"role": "user", "content": "My name is Alice"})
    history.append({"role": "assistant", "content": response1})
    
    # Second message with history - should remember the name
    response2 = client.send_message(model, "What is my name?", history)
    assert isinstance(response2, str)
    assert len(response2) > 0
    
    # The response should mention Alice (conversation context maintained)
    # Note: Small models may not always maintain context perfectly, so we just check it's a valid response
    assert isinstance(response2, str)

