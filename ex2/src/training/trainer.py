"""
Training module for LSTM signal extraction.

Handles training loop, loss calculation, and state management.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Optional
import numpy as np
from tqdm import tqdm

from ..model.lstm_model import ConditionalLSTM


class Trainer:
    """Handles LSTM model training."""
    
    def __init__(
        self,
        model: ConditionalLSTM,
        learning_rate: float = 0.001,
        device: Optional[torch.device] = None
    ):
        """
        Initialize trainer.
        
        Args:
            model: LSTM model to train
            learning_rate: Learning rate for optimizer
            device: Device to train on (CPU or CUDA)
        """
        self.model = model
        self.device = device if device is not None else torch.device('cpu')
        self.model.to(self.device)
        
        # Loss function: MSE
        self.criterion = nn.MSELoss()
        
        # Optimizer: Adam
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Learning rate scheduler: ReduceLROnPlateau
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5
        )
        
        # Training history
        self.history = {
            'train_loss': [],
            'mse_train': []
        }
    
    def train_epoch(
        self,
        train_loader: DataLoader,
        reset_state: bool = True,
        accumulation_steps: int = 100
    ) -> Dict[str, float]:
        """
        Train model for one epoch with gradient accumulation.
        
        Args:
            train_loader: Training data loader
            reset_state: Whether to reset LSTM state at start of epoch (default: True)
            accumulation_steps: Number of samples to accumulate gradients before update
        
        Returns:
            Dictionary with training metrics
        """
        self.model.train()
        total_loss = 0.0
        total_samples = 0
        accumulated_loss = 0.0
        
        # Detect if we're using sequences (3D input) or individual samples (2D input)
        sample_input, _ = next(iter(train_loader))
        is_sequence = sample_input.dim() == 3  # (batch, seq_len, features)
        
        # Initialize hidden state
        hidden_state = None
        prev_freq_selector = None
        
        # Zero gradients at start
        self.optimizer.zero_grad()
        
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            # Move to device
            inputs = inputs.to(self.device)
            targets = targets.to(self.device)
            
            if is_sequence:
                # Sequence processing: simpler, process entire sequences at once
                # Input shape: (batch_size, seq_len, input_size)
                # Target shape: (batch_size, seq_len)
                batch_size = inputs.size(0)
                
                # Forward pass through entire sequence
                output, _ = self.model(inputs, None)  # Reset state for each sequence
                
                # Calculate loss over entire sequence
                # output shape: (batch_size, seq_len, 1), need to squeeze last dim
                output = output.squeeze(-1)  # (batch_size, seq_len)
                loss = self.criterion(output, targets)
                
                # Normalize loss for accumulation
                loss = loss / accumulation_steps
                
                # Backward pass (accumulate gradients)
                loss.backward()
                
                # Accumulate loss for reporting
                accumulated_loss += loss.item() * accumulation_steps
                total_loss += loss.item() * accumulation_steps
                total_samples += 1
                
                # Update weights every accumulation_steps batches
                if total_samples % accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                    accumulated_loss = 0.0
            else:
                # Original individual sample processing
                # Ensure inputs have correct shape
                if inputs.dim() == 1:
                    inputs = inputs.unsqueeze(0)
                if targets.dim() == 0:
                    targets = targets.unsqueeze(0)
                
                batch_size = inputs.size(0)
                
                # Process each sample sequentially
                for i in range(batch_size):
                    input_sample = inputs[i:i+1]  # (1, input_size)
                    target_sample = targets[i:i+1]  # (1,)
                    
                    # Check if frequency changed (reset state if needed)
                    current_freq_selector = input_sample[0, 1:5]
                    if prev_freq_selector is not None:
                        if not torch.equal(current_freq_selector, prev_freq_selector):
                            # Frequency changed, reset state
                            hidden_state = None
                    prev_freq_selector = current_freq_selector.clone()
                    
                    # Initialize hidden state if needed
                    if hidden_state is None:
                        hidden_state = self.model.reset_state(batch_size=1, device=self.device)
                    
                    # Forward pass
                    output, hidden_state = self.model(input_sample, hidden_state)
                    
                    # Calculate loss
                    target_sample = target_sample.unsqueeze(1)  # (1, 1)
                    loss = self.criterion(output, target_sample)
                    
                    # Normalize loss for accumulation
                    loss = loss / accumulation_steps
                    
                    # Backward pass (accumulate gradients)
                    loss.backward()
                    
                    # Accumulate loss for reporting
                    accumulated_loss += loss.item() * accumulation_steps
                    total_loss += loss.item() * accumulation_steps
                    total_samples += 1
                    
                    # Update weights every accumulation_steps samples
                    if total_samples % accumulation_steps == 0:
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                        self.optimizer.step()
                        self.optimizer.zero_grad()
                        accumulated_loss = 0.0
                    
                    # Detach state to prevent memory issues
                    hidden_state = (hidden_state[0].detach(), hidden_state[1].detach())
        
        # Final update if there are remaining gradients
        if total_samples % accumulation_steps != 0:
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            self.optimizer.zero_grad()
        
        # Calculate average loss
        avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
        
        return {
            'loss': avg_loss,
            'samples': total_samples
        }
    
    def train(
        self,
        train_loader: DataLoader,
        num_epochs: int = 10,
        reset_state: bool = True,
        verbose: bool = True
    ) -> Dict[str, list]:
        """
        Train model for multiple epochs.
        
        Args:
            train_loader: Training data loader
            num_epochs: Number of training epochs
            reset_state: Whether to reset LSTM state between samples
            verbose: Whether to print training progress
        
        Returns:
            Training history dictionary
        """
        # Create main progress bar for epochs
        epoch_pbar = tqdm(range(num_epochs), desc="Epochs", ncols=120) if verbose else range(num_epochs)
        
        for epoch in epoch_pbar:
            # Train one epoch
            metrics = self.train_epoch(train_loader, reset_state=reset_state)
            
            # Calculate MSE_train
            mse_train = self.calculate_mse(train_loader, reset_state=reset_state)
            
            # Store history
            self.history['train_loss'].append(metrics['loss'])
            self.history['mse_train'].append(mse_train)
            
            # Update learning rate scheduler
            self.scheduler.step(mse_train)
            
            if verbose:
                current_lr = self.optimizer.param_groups[0]['lr']
                epoch_pbar.set_postfix({
                    'Loss': f'{metrics["loss"]:.6f}',
                    'MSE': f'{mse_train:.6f}',
                    'LR': f'{current_lr:.6f}'
                })
        
        if verbose:
            epoch_pbar.close()
        
        return self.history
    
    def calculate_mse(
        self,
        data_loader: DataLoader,
        reset_state: bool = True
    ) -> float:
        """
        Calculate Mean Squared Error on dataset.
        
        MSE = (1/N) * sum((LSTM(S[t], C) - Target[t])^2)
        
        Args:
            data_loader: Data loader for dataset
            reset_state: Whether to reset LSTM state between samples
        
        Returns:
            Mean Squared Error value
        """
        self.model.eval()
        total_squared_error = 0.0
        total_samples = 0
        
        # Detect if we're using sequences
        sample_input, _ = next(iter(data_loader))
        is_sequence = sample_input.dim() == 3
        
        # Initialize hidden state
        # For L=1, state should NOT be reset between consecutive samples
        hidden_state = None
        prev_freq_selector = None
        
        with torch.no_grad():
            for batch_idx, (inputs, targets) in enumerate(data_loader):
                # Move to device
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)
                
                if is_sequence:
                    # Sequence processing
                    # Input shape: (batch_size, seq_len, input_size)
                    # Target shape: (batch_size, seq_len)
                    batch_size = inputs.size(0)
                    seq_len = inputs.size(1)
                    
                    # Forward pass
                    output, _ = self.model(inputs, None)
                    
                    # Calculate squared error
                    # output shape: (batch_size, seq_len, 1), need to squeeze
                    output = output.squeeze(-1)  # (batch_size, seq_len)
                    squared_error = (output - targets) ** 2
                    
                    total_squared_error += squared_error.sum().item()
                    total_samples += batch_size * seq_len
                else:
                    # Original individual sample processing
                    # Ensure inputs have correct shape
                    if inputs.dim() == 1:
                        inputs = inputs.unsqueeze(0)
                    if targets.dim() == 0:
                        targets = targets.unsqueeze(0)
                    
                    batch_size = inputs.size(0)
                    
                    # Process each sample in the batch sequentially
                    for i in range(batch_size):
                        # Get single sample
                        input_sample = inputs[i:i+1]  # (1, input_size)
                        target_sample = targets[i:i+1]  # (1,)
                        
                        # Check if we're switching frequencies
                        current_freq_selector = input_sample[0, 1:5]
                        if prev_freq_selector is not None:
                            if not torch.equal(current_freq_selector, prev_freq_selector):
                                # Frequency changed, reset state
                                hidden_state = self.model.reset_state(batch_size=1, device=self.device)
                        prev_freq_selector = current_freq_selector.clone()
                        
                        # Initialize hidden state on first sample if needed
                        if hidden_state is None:
                            hidden_state = self.model.reset_state(batch_size=1, device=self.device)
                        
                        # For L=1, do NOT reset state between samples of the same frequency
                        # State is passed from previous sample to current sample
                        # Detach hidden state to break computation graph between samples
                        if hidden_state is not None:
                            hidden_state = (hidden_state[0].detach(), hidden_state[1].detach())
                        
                        # Forward pass
                        output, hidden_state = self.model(input_sample, hidden_state)
                        
                        # Calculate squared error
                        target_sample = target_sample.unsqueeze(1)  # (1, 1)
                        squared_error = (output - target_sample) ** 2
                        
                        total_squared_error += squared_error.item()
                        total_samples += 1
        
        # Calculate MSE
        mse = total_squared_error / total_samples if total_samples > 0 else 0.0
        
        return mse
    
    def save_model(self, filepath: str):
        """Save model checkpoint."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'history': self.history
        }, filepath)
    
    def load_model(self, filepath: str):
        """Load model checkpoint."""
        checkpoint = torch.load(filepath)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.history = checkpoint.get('history', {'train_loss': [], 'mse_train': []})

