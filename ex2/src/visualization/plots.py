"""
Visualization module for LSTM signal extraction.

Generates graphs comparing predictions vs targets.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Optional
import os


def plot_single_frequency_comparison(
    target: np.ndarray,
    prediction: np.ndarray,
    mixed_signal: np.ndarray,
    time: np.ndarray,
    frequency_idx: int,
    frequency_value: float,
    save_path: Optional[str] = None
):
    """
    Plot comparison for a single frequency (Graph 1 style).
    
    Shows Target_i, LSTM Output (points), and S (mixed noisy signal).
    
    Args:
        target: Pure target signal array
        prediction: LSTM prediction array
        mixed_signal: Mixed noisy input signal array
        time: Time vector array
        frequency_idx: Frequency index (0-3)
        frequency_value: Frequency value in Hz
        save_path: Optional path to save figure
    """
    plt.figure(figsize=(12, 6))
    
    # Plot target (pure signal)
    plt.plot(time, target, 'b-', label=f'Target_{frequency_idx+1} (Pure)', linewidth=2)
    
    # Plot LSTM output (as points)
    plt.plot(time, prediction, 'r.', label='LSTM Output', markersize=2, alpha=0.6)
    
    # Plot mixed noisy signal (chaotic background)
    plt.plot(time, mixed_signal, 'g-', label='S (Mixed Noisy Input)', linewidth=0.5, alpha=0.3)
    
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Amplitude', fontsize=12)
    plt.title(f'Frequency Extraction: f{frequency_idx+1} = {frequency_value} Hz', fontsize=14)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    return plt.gcf()


def plot_all_frequencies(
    targets: np.ndarray,
    predictions: np.ndarray,
    mixed_signal: np.ndarray,
    time: np.ndarray,
    frequencies: list,
    save_path: Optional[str] = None
):
    """
    Plot all 4 extracted frequencies (Graph 2 style).
    
    Creates 4 subplots, one for each frequency component.
    
    Args:
        targets: Pure target signals array of shape (4, num_samples)
        predictions: LSTM predictions array of shape (4, num_samples)
        mixed_signal: Mixed noisy input signal array
        time: Time vector array
        frequencies: List of 4 frequency values in Hz
        save_path: Optional path to save figure
    """
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    
    for freq_idx in range(4):
        ax = axes[freq_idx]
        
        # Plot target (pure signal)
        ax.plot(time, targets[freq_idx], 'b-', label=f'Target_{freq_idx+1} (Pure)', linewidth=2)
        
        # Plot LSTM output (as points)
        ax.plot(time, predictions[freq_idx], 'r.', label='LSTM Output', markersize=1.5, alpha=0.6)
        
        # Plot mixed noisy signal (chaotic background)
        ax.plot(time, mixed_signal, 'g-', label='S (Mixed Noisy Input)', linewidth=0.5, alpha=0.3)
        
        ax.set_xlabel('Time (seconds)', fontsize=10)
        ax.set_ylabel('Amplitude', fontsize=10)
        ax.set_title(f'Frequency f{freq_idx+1} = {frequencies[freq_idx]} Hz', fontsize=12)
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    return fig


def plot_training_history(
    history: dict,
    save_path: Optional[str] = None
):
    """
    Plot training history (loss and MSE over epochs).
    
    Args:
        history: Dictionary with 'train_loss' and 'mse_train' lists
        save_path: Optional path to save figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    epochs = range(1, len(history['train_loss']) + 1)
    
    # Plot training loss
    ax1.plot(epochs, history['train_loss'], 'b-', label='Training Loss', linewidth=2)
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Loss', fontsize=12)
    ax1.set_title('Training Loss', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot MSE_train
    ax2.plot(epochs, history['mse_train'], 'r-', label='MSE_train', linewidth=2)
    ax2.set_xlabel('Epoch', fontsize=12)
    ax2.set_ylabel('MSE', fontsize=12)
    ax2.set_title('MSE on Training Set', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    return fig


def plot_mse_comparison(
    mse_train: float,
    mse_test: float,
    save_path: Optional[str] = None
):
    """
    Plot comparison of MSE_train and MSE_test.
    
    Args:
        mse_train: Training set MSE
        mse_test: Test set MSE
        save_path: Optional path to save figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    categories = ['Training Set', 'Test Set']
    mse_values = [mse_train, mse_test]
    colors = ['blue', 'red']
    
    bars = ax.bar(categories, mse_values, color=colors, alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar, value in zip(bars, mse_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.6f}',
                ha='center', va='bottom', fontsize=12)
    
    ax.set_ylabel('MSE', fontsize=12)
    ax.set_title('MSE Comparison: Training vs Test Set', fontsize=14)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add generalization status
    relative_diff = abs(mse_test - mse_train) / max(mse_train, 1e-10)
    if relative_diff <= 0.1:
        status = "✓ Good Generalization"
        color = 'green'
    else:
        status = "✗ Poor Generalization"
        color = 'red'
    
    ax.text(0.5, 0.95, status, transform=ax.transAxes,
            ha='center', fontsize=12, color=color, weight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    return fig


def create_all_plots(
    targets: np.ndarray,
    predictions: np.ndarray,
    mixed_signal: np.ndarray,
    time: np.ndarray,
    frequencies: list,
    history: dict,
    mse_train: float,
    mse_test: float,
    output_dir: str = 'outputs/plots'
):
    """
    Create all required plots and save them.
    
    Args:
        targets: Pure target signals array of shape (4, num_samples)
        predictions: LSTM predictions array of shape (4, num_samples)
        mixed_signal: Mixed noisy input signal array
        time: Time vector array
        frequencies: List of 4 frequency values in Hz
        history: Training history dictionary
        mse_train: Training set MSE
        mse_test: Test set MSE
        output_dir: Directory to save plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot 1: Single frequency comparison (f2 as example)
    plot_single_frequency_comparison(
        targets[1], predictions[1], mixed_signal, time,
        frequency_idx=1, frequency_value=frequencies[1],
        save_path=os.path.join(output_dir, 'single_frequency_comparison.png')
    )
    
    # Plot 2: All 4 frequencies
    plot_all_frequencies(
        targets, predictions, mixed_signal, time, frequencies,
        save_path=os.path.join(output_dir, 'all_frequencies.png')
    )
    
    # Plot 3: Training history
    plot_training_history(
        history,
        save_path=os.path.join(output_dir, 'training_history.png')
    )
    
    # Plot 4: MSE comparison
    plot_mse_comparison(
        mse_train, mse_test,
        save_path=os.path.join(output_dir, 'mse_comparison.png')
    )
    
    print(f"All plots saved to {output_dir}")

