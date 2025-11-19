"""
LSTM model for conditional signal extraction.

The model extracts individual frequency components from mixed noisy signals
using a one-hot encoded frequency selector.
"""

import torch
import torch.nn as nn
from typing import Tuple, Optional


class ConditionalLSTM(nn.Module):
    """
    LSTM model for conditional regression.
    
    Takes input [S[t], C1, C2, C3, C4] where:
    - S[t]: Mixed noisy signal at time t
    - C: One-hot encoded frequency selector
    
    Outputs: Predicted target frequency value Target_i[t]
    """
    
    def __init__(
        self,
        input_size: int = 5,
        hidden_size: int = 64,
        num_layers: int = 1,
        dropout: float = 0.0
    ):
        """
        Initialize LSTM model.
        
        Args:
            input_size: Input dimension (5: 1 signal + 4 one-hot selector)
            hidden_size: LSTM hidden state size
            num_layers: Number of LSTM layers
            dropout: Dropout probability (0.0 for single layer)
        """
        super(ConditionalLSTM, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        
        # Output layer: maps hidden state to scalar output
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(
        self,
        x: torch.Tensor,
        hidden_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass through LSTM.
        
        Args:
            x: Input tensor of shape (batch_size, seq_len, input_size) or (batch_size, input_size)
            hidden_state: Optional tuple of (h_t, c_t) for state management
        
        Returns:
            Tuple of (output, (h_t, c_t)) where:
            - output: Predicted target value(s)
                     Shape (batch_size, 1) if seq_len=1
                     Shape (batch_size, seq_len, 1) if seq_len>1
            - hidden_state: Tuple of (h_t, c_t) for next iteration
        """
        # Ensure input has sequence dimension
        if x.dim() == 2:
            # Add sequence dimension: (batch_size, input_size) -> (batch_size, 1, input_size)
            x = x.unsqueeze(1)
        
        # LSTM forward pass
        # lstm_out shape: (batch_size, seq_len, hidden_size)
        lstm_out, hidden_state = self.lstm(x, hidden_state)
        
        # Get sequence length
        seq_len = lstm_out.size(1)
        
        if seq_len == 1:
            # For single timestep: extract last (only) timestep
            last_hidden = lstm_out[:, -1, :]  # (batch_size, hidden_size)
            output = self.fc(last_hidden)  # (batch_size, 1)
        else:
            # For multiple timesteps: map ALL timesteps to outputs
            # Reshape to apply fc layer to all timesteps at once
            batch_size = lstm_out.size(0)
            lstm_out_flat = lstm_out.reshape(batch_size * seq_len, self.hidden_size)
            output_flat = self.fc(lstm_out_flat)  # (batch_size * seq_len, 1)
            output = output_flat.reshape(batch_size, seq_len, 1)  # (batch_size, seq_len, 1)
        
        return output, hidden_state
    
    def reset_state(self, batch_size: int = 1, device: Optional[torch.device] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Reset LSTM hidden state to zeros.
        
        For L=1 sequence length, state must be reset between samples
        to allow temporal dependency learning.
        
        Args:
            batch_size: Batch size
            device: Device to create tensors on
        
        Returns:
            Tuple of (h_0, c_0) initialized to zeros
        """
        if device is None:
            device = next(self.parameters()).device
        
        h_0 = torch.zeros(
            self.num_layers,
            batch_size,
            self.hidden_size,
            device=device
        )
        
        c_0 = torch.zeros(
            self.num_layers,
            batch_size,
            self.hidden_size,
            device=device
        )
        
        return (h_0, c_0)
    
    def predict_single(
        self,
        x: torch.Tensor,
        reset_state: bool = True
    ) -> torch.Tensor:
        """
        Predict single sample with optional state reset.
        
        Args:
            x: Input tensor of shape (1, input_size) or (input_size,)
            reset_state: Whether to reset state before prediction
        
        Returns:
            Predicted value (scalar tensor)
        """
        if x.dim() == 1:
            x = x.unsqueeze(0)  # Add batch dimension
        
        # Reset state if requested (critical for L=1)
        hidden_state = None
        if reset_state:
            hidden_state = self.reset_state(batch_size=1, device=x.device)
        
        # Forward pass
        with torch.no_grad():
            output, _ = self.forward(x, hidden_state)
        
        return output.squeeze()

