"""
Unit tests for dataset generation.
"""

import pytest
import numpy as np
from src.data.dataset import SignalDataset


def test_dataset_initialization():
    """Test dataset initialization with default parameters."""
    dataset = SignalDataset()
    
    assert len(dataset.frequencies) == 4
    assert dataset.frequencies == [1.0, 3.0, 5.0, 7.0]
    assert dataset.fs == 1000.0
    assert dataset.duration == 10.0
    assert dataset.num_samples == 10000
    assert dataset.seed == 1


def test_dataset_custom_parameters():
    """Test dataset initialization with custom parameters."""
    frequencies = [2.0, 4.0, 6.0, 8.0]
    sampling_rate = 500.0
    duration = 5.0
    seed = 42
    
    dataset = SignalDataset(
        frequencies=frequencies,
        sampling_rate=sampling_rate,
        duration=duration,
        seed=seed
    )
    
    assert dataset.frequencies == frequencies
    assert dataset.fs == sampling_rate
    assert dataset.duration == duration
    assert dataset.seed == seed
    assert dataset.num_samples == int(sampling_rate * duration)


def test_generate_noisy_signal():
    """Test noisy signal generation."""
    dataset = SignalDataset(seed=1)
    noisy_signal = dataset.generate_noisy_signal(frequency=1.0)
    
    # Check shape
    assert noisy_signal.shape == (dataset.num_samples,)
    
    # Check value range (should be bounded due to amplitude and phase noise)
    assert np.all(np.abs(noisy_signal) <= 1.5)  # Max amplitude * max sin value
    
    # Check that signal varies (not constant)
    assert np.std(noisy_signal) > 0.1


def test_generate_mixed_signal():
    """Test mixed signal generation."""
    dataset = SignalDataset(seed=1)
    mixed_signal = dataset.generate_mixed_signal()
    
    # Check shape
    assert mixed_signal.shape == (dataset.num_samples,)
    
    # Check value range
    assert np.all(np.abs(mixed_signal) <= 1.5)
    
    # Check that signal varies
    assert np.std(mixed_signal) > 0.1


def test_generate_pure_target():
    """Test pure target generation."""
    dataset = SignalDataset(seed=1)
    pure_target = dataset.generate_pure_target(frequency=1.0)
    
    # Check shape
    assert pure_target.shape == (dataset.num_samples,)
    
    # Check value range (pure sine should be in [-1, 1])
    assert np.all(pure_target >= -1.0)
    assert np.all(pure_target <= 1.0)
    
    # Check that it's a sine wave (should have specific pattern)
    assert np.abs(pure_target[0]) < 0.1  # sin(0) ≈ 0


def test_generate_dataset():
    """Test complete dataset generation."""
    dataset = SignalDataset(seed=1)
    inputs, targets = dataset.generate_dataset()
    
    # Check shapes
    assert inputs.shape == (40000, 5)  # 10000 samples × 4 frequencies
    assert targets.shape == (40000,)
    
    # Check input structure: [S[t], C1, C2, C3, C4]
    # First element should be signal value
    assert np.all(np.abs(inputs[:, 0]) <= 1.5)
    
    # Last 4 elements should be one-hot encoded
    one_hot = inputs[:, 1:5]
    assert np.all((one_hot == 0) | (one_hot == 1))  # Binary values
    assert np.all(np.sum(one_hot, axis=1) == 1)  # Exactly one 1 per row
    
    # Check targets range
    assert np.all(targets >= -1.0)
    assert np.all(targets <= 1.0)


def test_dataset_seed_reproducibility():
    """Test that same seed produces same results."""
    dataset1 = SignalDataset(seed=42)
    dataset2 = SignalDataset(seed=42)
    
    inputs1, targets1 = dataset1.generate_dataset()
    inputs2, targets2 = dataset2.generate_dataset()
    
    # Should be identical with same seed
    np.testing.assert_array_equal(inputs1, inputs2)
    np.testing.assert_array_equal(targets1, targets2)


def test_dataset_different_seeds():
    """Test that different seeds produce different results."""
    dataset1 = SignalDataset(seed=1)
    dataset2 = SignalDataset(seed=2)
    
    inputs1, targets1 = dataset1.generate_dataset()
    inputs2, targets2 = dataset2.generate_dataset()
    
    # Should be different with different seeds
    assert not np.array_equal(inputs1, inputs2)
    assert not np.array_equal(targets1, targets2)


def test_get_info():
    """Test dataset info retrieval."""
    dataset = SignalDataset(seed=1)
    info = dataset.get_info()
    
    assert 'frequencies' in info
    assert 'sampling_rate' in info
    assert 'duration' in info
    assert 'num_samples' in info
    assert 'total_dataset_size' in info
    assert 'seed' in info
    assert info['total_dataset_size'] == 40000

