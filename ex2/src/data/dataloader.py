"""
PyTorch Dataset and DataLoader wrappers for signal data.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import Tuple, Optional
import numpy as np
import os

from .dataset import SignalDataset


class SignalPyTorchDataset(Dataset):
    """PyTorch Dataset wrapper for signal data."""
    
    def __init__(self, inputs: np.ndarray, targets: np.ndarray):
        """
        Initialize PyTorch dataset.
        
        Args:
            inputs: Input data array of shape (N, 5) or (N, L, 5)
            targets: Target data array of shape (N,) or (N, L)
        """
        self.inputs = torch.FloatTensor(inputs)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.inputs)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get a single sample.
        
        Args:
            idx: Sample index
            
        Returns:
            Tuple of (input, target) tensors
        """
        return self.inputs[idx], self.targets[idx]


def create_dataloaders(
    train_seed: int = 1,
    test_seed: int = 2,
    batch_size: int = 1,
    shuffle: bool = False,
    sequence_length: int = 1,
    train_data_path: Optional[str] = None,
    test_data_path: Optional[str] = None,
    **dataset_kwargs
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and test dataloaders.
    
    Args:
        train_seed: Random seed for training set
        test_seed: Random seed for test set
        batch_size: Batch size for DataLoader
        shuffle: Whether to shuffle data
        sequence_length: Length of sequences (L). Default is 1.
        train_data_path: Optional path to load saved training dataset
        test_data_path: Optional path to load saved test dataset
        **dataset_kwargs: Additional arguments for SignalDataset
        
    Returns:
        Tuple of (train_loader, test_loader)
    """
    # Load or generate training dataset
    if train_data_path and os.path.exists(train_data_path):
        train_inputs, train_targets, _ = SignalDataset.load_dataset(train_data_path)
        train_dataset = SignalPyTorchDataset(train_inputs, train_targets)
    else:
        train_dataset_gen = SignalDataset(seed=train_seed, **dataset_kwargs)
        train_inputs, train_targets = train_dataset_gen.generate_dataset(sequence_length=sequence_length)
        train_dataset = SignalPyTorchDataset(train_inputs, train_targets)
    
    # Load or generate test dataset
    if test_data_path and os.path.exists(test_data_path):
        test_inputs, test_targets, _ = SignalDataset.load_dataset(test_data_path)
        test_dataset = SignalPyTorchDataset(test_inputs, test_targets)
    else:
        test_dataset_gen = SignalDataset(seed=test_seed, **dataset_kwargs)
        test_inputs, test_targets = test_dataset_gen.generate_dataset(sequence_length=sequence_length)
        test_dataset = SignalPyTorchDataset(test_inputs, test_targets)
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )
    
    return train_loader, test_loader

