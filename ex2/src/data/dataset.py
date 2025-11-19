"""
Dataset generation for LSTM signal extraction.

Generates clean mixed signals and pure targets for training and testing.
No noise is added to the signals.
"""

import numpy as np
import os
import pickle
from typing import Tuple, Optional


class SignalDataset:
    """Generates clean mixed signals and pure targets for LSTM training."""
    
    def __init__(
        self,
        frequencies: list = [1.0, 3.0, 5.0, 7.0],
        sampling_rate: float = 1000.0,
        duration: float = 10.0,
        seed: int = 1
    ):
        """
        Initialize dataset generator.
        
        Args:
            frequencies: List of 4 frequencies in Hz [f1, f2, f3, f4]
            sampling_rate: Sampling rate in Hz (Fs)
            duration: Signal duration in seconds
            seed: Random seed for reproducibility
        """
        self.frequencies = frequencies
        self.fs = sampling_rate
        self.duration = duration
        self.seed = seed
        
        # Calculate number of samples
        self.num_samples = int(sampling_rate * duration)
        
        # Time vector
        self.t = np.linspace(0, duration, self.num_samples, endpoint=False)
        
        # Set random seed
        np.random.seed(seed)
    
    def generate_clean_signal(self, frequency: float) -> np.ndarray:
        """
        Generate clean (pure) sine wave for a given frequency.
        
        Signal(t) = sin(2π * f * t)
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            Clean sine wave signal array
        """
        return np.sin(2 * np.pi * frequency * self.t)
    
    def generate_noisy_signal(self, frequency: float) -> np.ndarray:
        """
        Generate noisy sine wave with random phase offset and additive noise.
        
        Sinus_i^noisy(t) = sin(2π * f_i * t + φ_i) + N(t)
        where:
        - φ_i ~ Uniform(0, 2π) is a fixed random phase offset per frequency
        - N(t) ~ Normal(0, 0.05) is additive Gaussian noise (reduced for easier learning)
        
        This preserves frequency structure while adding noise.
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            Noisy sine wave signal array
        """
        # Generate one random phase offset for this frequency: Uniform(0, 2π)
        phase_offset = np.random.uniform(0, 2 * np.pi)
        
        # Create clean signal with random phase offset
        clean_signal = np.sin(2 * np.pi * frequency * self.t + phase_offset)
        
        # Add Gaussian noise: N(0, 0.05) - reduced for easier learning
        noise = np.random.normal(0, 0.05, size=self.num_samples)
        
        # Noisy signal = clean + noise
        noisy_signal = clean_signal + noise
        
        return noisy_signal
    
    def generate_mixed_signal(self, normalize: bool = True) -> np.ndarray:
        """
        Generate mixed noisy signal S(t) - sum of all noisy frequency components.
        
        S(t) = (1/4) * sum(Sinus_i^noisy(t)) for i=1 to 4
        Each component has random amplitude and phase noise at each sample.
        Optionally normalized to zero mean and unit variance.
        
        Args:
            normalize: Whether to normalize the signal (default: True)
        
        Returns:
            Mixed noisy signal array
        """
        # Generate noisy signals for each frequency
        noisy_signals = []
        for freq in self.frequencies:
            noisy_signal = self.generate_noisy_signal(freq)
            noisy_signals.append(noisy_signal)
        
        # Sum and normalize (average)
        mixed_signal = np.sum(noisy_signals, axis=0) / 4.0
        
        # Normalize to zero mean and unit variance for easier learning
        if normalize:
            mean = np.mean(mixed_signal)
            std = np.std(mixed_signal)
            if std > 1e-8:
                mixed_signal = (mixed_signal - mean) / std
        
        return mixed_signal
    
    def generate_pure_target(self, frequency: float) -> np.ndarray:
        """
        Generate pure (noiseless) target signal.
        
        Target_i(t) = sin(2π * f_i * t)
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            Pure sine wave signal array
        """
        pure_signal = np.sin(2 * np.pi * frequency * self.t)
        return pure_signal
    
    def generate_dataset(self, sequence_length: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate complete dataset with inputs and targets.
        
        Creates sequences for training. 
        - If sequence_length=1: 40,000 individual samples (10,000 time points × 4 frequencies)
        - If sequence_length>1: Creates overlapping sequences for each frequency
        
        Each sample: [S[t], C1, C2, C3, C4] -> Target_i[t]
        - S[t]: Mixed noisy signal (sum of 4 noisy frequency components, normalized)
        - Target_i[t]: Pure (noiseless) signal for frequency i
        
        Args:
            sequence_length: Length of sequences (L). Default is 1.
        
        Returns:
            Tuple of (inputs, targets) where:
            - If L=1: inputs shape (40000, 5), targets shape (40000,)
            - If L>1: inputs shape (N, L, 5), targets shape (N, L)
                     where N = num_sequences_per_freq × 4
        """
        # Generate pure target signals for each frequency (clean, no noise)
        pure_signals = []
        for freq in self.frequencies:
            signal = self.generate_pure_target(freq)
            pure_signals.append(signal)
        pure_signals = np.array(pure_signals)  # Shape: (4, num_samples)
        
        # Generate mixed noisy signal: average of all noisy frequency components (normalized)
        mixed_signal = self.generate_mixed_signal(normalize=True)
        
        if sequence_length == 1:
            # Original implementation: individual samples
            inputs = []
            targets = []
            
            # For each frequency, process all time points sequentially
            for freq_idx in range(4):
                # Create one-hot encoded frequency selector
                one_hot = np.zeros(4)
                one_hot[freq_idx] = 1.0
                
                # For each time point, create a sample for this frequency
                for t_idx in range(self.num_samples):
                    # Input: [S[t], C1, C2, C3, C4] where S[t] is the mixed signal
                    input_vector = np.concatenate([[mixed_signal[t_idx]], one_hot])
                    inputs.append(input_vector)
                    
                    # Target: Target_i[t] - the pure signal for this frequency
                    target_value = pure_signals[freq_idx, t_idx]
                    targets.append(target_value)
            
            inputs = np.array(inputs)  # Shape: (40000, 5)
            targets = np.array(targets)  # Shape: (40000,)
        else:
            # Sequence-based implementation: create overlapping sequences
            inputs = []
            targets = []
            
            # For each frequency
            for freq_idx in range(4):
                # Create one-hot encoded frequency selector
                one_hot = np.zeros(4)
                one_hot[freq_idx] = 1.0
                
                # Create sequences by sliding window
                num_sequences = self.num_samples - sequence_length + 1
                for start_idx in range(num_sequences):
                    end_idx = start_idx + sequence_length
                    
                    # Create sequence of inputs
                    sequence_inputs = []
                    sequence_targets = []
                    for t_idx in range(start_idx, end_idx):
                        # Input: [S[t], C1, C2, C3, C4]
                        input_vector = np.concatenate([[mixed_signal[t_idx]], one_hot])
                        sequence_inputs.append(input_vector)
                        
                        # Target: Target_i[t]
                        target_value = pure_signals[freq_idx, t_idx]
                        sequence_targets.append(target_value)
                    
                    inputs.append(sequence_inputs)
                    targets.append(sequence_targets)
            
            inputs = np.array(inputs)  # Shape: (N, L, 5)
            targets = np.array(targets)  # Shape: (N, L)
        
        return inputs, targets
    
    def get_info(self) -> dict:
        """Get dataset information."""
        return {
            'frequencies': self.frequencies,
            'sampling_rate': self.fs,
            'duration': self.duration,
            'num_samples': self.num_samples,
            'total_dataset_size': self.num_samples * len(self.frequencies),
            'seed': self.seed
        }
    
    def save_dataset(self, filepath: str, inputs: np.ndarray, targets: np.ndarray):
        """
        Save generated dataset to disk.
        
        Args:
            filepath: Path to save the dataset
            inputs: Input data array
            targets: Target data array
        """
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        # Generate pure signals for saving
        pure_signals = np.array([self.generate_pure_target(f) for f in self.frequencies])
        
        # Extract mixed signal from inputs (first column of inputs)
        # The mixed signal was already generated and is stored in inputs[:, 0]
        mixed_signal = inputs[::4, 0]  # Take every 4th sample (all same for different freqs)
        
        data = {
            'inputs': inputs,
            'targets': targets,
            'info': self.get_info(),
            'time': self.t,
            'mixed_signal': mixed_signal,
            'pure_signals': pure_signals
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Dataset saved to {filepath}")
    
    @staticmethod
    def load_dataset(filepath: str) -> Tuple[np.ndarray, np.ndarray, dict]:
        """
        Load dataset from disk.
        
        Args:
            filepath: Path to load the dataset from
        
        Returns:
            Tuple of (inputs, targets, info_dict)
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        print(f"Dataset loaded from {filepath}")
        return data['inputs'], data['targets'], data['info']

