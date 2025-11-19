"""
Unit tests for LSTM model.
"""

import pytest
import torch
import numpy as np
from src.model.lstm_model import ConditionalLSTM


def test_model_initialization():
    """Test model initialization with default parameters."""
    model = ConditionalLSTM()
    
    assert model.input_size == 5
    assert model.hidden_size == 64
    assert model.num_layers == 1


def test_model_custom_parameters():
    """Test model initialization with custom parameters."""
    input_size = 5
    hidden_size = 128
    num_layers = 2
    
    model = ConditionalLSTM(
        input_size=input_size,
        hidden_size=hidden_size,
        num_layers=num_layers
    )
    
    assert model.input_size == input_size
    assert model.hidden_size == hidden_size
    assert model.num_layers == num_layers


def test_model_forward_pass():
    """Test model forward pass."""
    model = ConditionalLSTM(input_size=5, hidden_size=64)
    model.eval()
    
    # Create input: [S[t], C1, C2, C3, C4]
    batch_size = 1
    input_tensor = torch.randn(batch_size, 5)
    
    # Forward pass
    output, hidden_state = model(input_tensor)
    
    # Check output shape
    assert output.shape == (batch_size, 1)
    
    # Check hidden state structure
    assert isinstance(hidden_state, tuple)
    assert len(hidden_state) == 2
    h_t, c_t = hidden_state
    assert h_t.shape == (1, batch_size, 64)  # (num_layers, batch_size, hidden_size)
    assert c_t.shape == (1, batch_size, 64)


def test_model_forward_pass_batch():
    """Test model forward pass with batch."""
    model = ConditionalLSTM(input_size=5, hidden_size=64)
    model.eval()
    
    batch_size = 4
    input_tensor = torch.randn(batch_size, 5)
    
    output, hidden_state = model(input_tensor)
    
    assert output.shape == (batch_size, 1)
    h_t, c_t = hidden_state
    assert h_t.shape == (1, batch_size, 64)
    assert c_t.shape == (1, batch_size, 64)


def test_model_reset_state():
    """Test state reset functionality."""
    model = ConditionalLSTM(input_size=5, hidden_size=64)
    
    batch_size = 1
    h_0, c_0 = model.reset_state(batch_size=batch_size)
    
    # Check state shapes
    assert h_0.shape == (1, batch_size, 64)
    assert c_0.shape == (1, batch_size, 64)
    
    # Check that state is zeros
    assert torch.all(h_0 == 0)
    assert torch.all(c_0 == 0)


def test_model_reset_state_custom_batch():
    """Test state reset with custom batch size."""
    model = ConditionalLSTM(input_size=5, hidden_size=64)
    
    batch_size = 8
    h_0, c_0 = model.reset_state(batch_size=batch_size)
    
    assert h_0.shape == (1, batch_size, 64)
    assert c_0.shape == (1, batch_size, 64)


def test_model_predict_single():
    """Test single prediction."""
    model = ConditionalLSTM(input_size=5, hidden_size=64)
    model.eval()
    
    # Create input vector
    input_vector = torch.randn(5)
    
    # Predict
    output = model.predict_single(input_vector, reset_state=True)
    
    # Check output is scalar
    assert output.dim() == 0 or output.shape == (1,)


def test_model_state_management():
    """Test that state can be passed between forward passes."""
    model = ConditionalLSTM(input_size=5, hidden_size=64)
    model.eval()
    
    # First forward pass
    input1 = torch.randn(1, 5)
    output1, hidden_state1 = model(input1)
    
    # Second forward pass with previous state
    input2 = torch.randn(1, 5)
    output2, hidden_state2 = model(input2, hidden_state1)
    
    # Check outputs are valid
    assert output1.shape == (1, 1)
    assert output2.shape == (1, 1)
    
    # Check hidden states are valid
    assert hidden_state1[0].shape == (1, 1, 64)
    assert hidden_state2[0].shape == (1, 1, 64)


def test_model_with_one_hot_input():
    """Test model with proper one-hot encoded input."""
    model = ConditionalLSTM(input_size=5, hidden_size=64)
    model.eval()
    
    # Create input with one-hot encoding: [S[t], 1, 0, 0, 0]
    signal_value = 0.5
    one_hot = torch.tensor([1.0, 0.0, 0.0, 0.0])
    input_tensor = torch.cat([torch.tensor([signal_value]), one_hot]).unsqueeze(0)
    
    output, _ = model(input_tensor)
    
    assert output.shape == (1, 1)
    assert not torch.isnan(output)


def test_model_gradient_flow():
    """Test that gradients can flow through the model."""
    model = ConditionalLSTM(input_size=5, hidden_size=64)
    model.train()
    
    input_tensor = torch.randn(1, 5, requires_grad=True)
    target = torch.randn(1, 1)
    
    output, _ = model(input_tensor)
    loss = torch.nn.functional.mse_loss(output, target)
    loss.backward()
    
    # Check that gradients exist
    assert input_tensor.grad is not None
    assert not torch.all(input_tensor.grad == 0)

