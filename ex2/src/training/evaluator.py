"""
Evaluation module for LSTM signal extraction.

Handles test set evaluation and generalization checking.
"""

import torch
from torch.utils.data import DataLoader
from typing import Dict, Tuple, Optional
import numpy as np

from ..model.lstm_model import ConditionalLSTM
from .trainer import Trainer


class Evaluator:
    """Handles model evaluation and generalization checking."""
    
    def __init__(
        self,
        model: ConditionalLSTM,
        device: Optional[torch.device] = None
    ):
        """
        Initialize evaluator.
        
        Args:
            model: Trained LSTM model
            device: Device to evaluate on (CPU or CUDA)
        """
        self.model = model
        self.device = device if device is not None else torch.device('cpu')
        self.model.to(self.device)
    
    def evaluate(
        self,
        test_loader: DataLoader,
        reset_state: bool = True
    ) -> Dict[str, float]:
        """
        Evaluate model on test set.
        
        Calculates MSE_test = (1/N) * sum((LSTM(S_test[t], C) - Target[t])^2)
        
        Args:
            test_loader: Test data loader
            reset_state: Whether to reset LSTM state between samples
        
        Returns:
            Dictionary with evaluation metrics
        """
        self.model.eval()
        total_squared_error = 0.0
        total_samples = 0
        
        # Initialize hidden state
        # For L=1, state should NOT be reset between consecutive samples
        hidden_state = None
        prev_freq_selector = None
        
        with torch.no_grad():
            for batch_idx, (inputs, targets) in enumerate(test_loader):
                # Move to device
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)
                
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
        
        # Calculate MSE_test
        mse_test = total_squared_error / total_samples if total_samples > 0 else 0.0
        
        return {
            'mse_test': mse_test,
            'total_samples': total_samples
        }
    
    def check_generalization(
        self,
        mse_train: float,
        mse_test: float,
        tolerance: float = 0.1
    ) -> Dict[str, any]:
        """
        Check model generalization.
        
        If MSE_test ≈ MSE_train, the model generalizes well.
        
        Args:
            mse_train: Training set MSE
            mse_test: Test set MSE
            tolerance: Relative tolerance for comparison (default 10%)
        
        Returns:
            Dictionary with generalization metrics and status
        """
        # Calculate relative difference
        relative_diff = abs(mse_test - mse_train) / max(mse_train, 1e-10)
        
        # Check if they are approximately equal
        generalizes_well = relative_diff <= tolerance
        
        return {
            'mse_train': mse_train,
            'mse_test': mse_test,
            'relative_difference': relative_diff,
            'generalizes_well': generalizes_well,
            'tolerance': tolerance
        }
    
    def predict_all_frequencies(
        self,
        mixed_signal: np.ndarray,
        reset_state: bool = True
    ) -> np.ndarray:
        """
        Predict all 4 frequency components from mixed signal.
        
        Args:
            mixed_signal: Mixed noisy signal array of shape (num_samples,)
            reset_state: Whether to reset LSTM state between samples
        
        Returns:
            Array of shape (4, num_samples) with predictions for each frequency
        """
        self.model.eval()
        num_samples = len(mixed_signal)
        predictions = np.zeros((4, num_samples))
        
        # Initialize hidden state
        # For L=1, state should NOT be reset between consecutive samples
        hidden_state = None
        if reset_state:
            # Reset state only at the start
            hidden_state = self.model.reset_state(batch_size=1, device=self.device)
        
        with torch.no_grad():
            for t in range(num_samples):
                # For each frequency
                for freq_idx in range(4):
                    # Create one-hot encoded frequency selector
                    one_hot = np.zeros(4)
                    one_hot[freq_idx] = 1.0
                    
                    # Create input: [S[t], C1, C2, C3, C4]
                    input_vector = np.concatenate([[mixed_signal[t]], one_hot])
                    input_tensor = torch.FloatTensor(input_vector).unsqueeze(0).to(self.device)
                    
                    # For L=1, do NOT reset state between samples
                    # State is passed from previous sample to current sample
                    # Detach hidden state to break computation graph between samples
                    if hidden_state is not None:
                        hidden_state = (hidden_state[0].detach(), hidden_state[1].detach())
                    
                    # Forward pass
                    output, hidden_state = self.model(input_tensor, hidden_state)
                    
                    # Store prediction
                    predictions[freq_idx, t] = output.cpu().item()
        
        return predictions
    
    def evaluate_full_pipeline(
        self,
        train_loader: DataLoader,
        test_loader: DataLoader,
        reset_state: bool = True
    ) -> Dict[str, any]:
        """
        Evaluate full pipeline: calculate MSE_train, MSE_test, and check generalization.
        
        Args:
            train_loader: Training data loader
            test_loader: Test data loader
            reset_state: Whether to reset LSTM state between samples
        
        Returns:
            Dictionary with all evaluation metrics
        """
        # Calculate MSE_train
        trainer = Trainer(self.model, device=self.device)
        mse_train = trainer.calculate_mse(train_loader, reset_state=reset_state)
        
        # Calculate MSE_test
        eval_results = self.evaluate(test_loader, reset_state=reset_state)
        mse_test = eval_results['mse_test']
        
        # Check generalization
        gen_results = self.check_generalization(mse_train, mse_test)
        
        return {
            'mse_train': mse_train,
            'mse_test': mse_test,
            'generalization': gen_results
        }

