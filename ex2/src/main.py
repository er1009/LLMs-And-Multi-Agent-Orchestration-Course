"""
Main entry point for LSTM signal extraction.

Orchestrates the full pipeline: data generation → model creation → training → evaluation → visualization.
"""

import torch
import numpy as np
import os
import argparse

from src.data.dataloader import create_dataloaders
from src.model.lstm_model import ConditionalLSTM
from src.training.trainer import Trainer
from src.training.evaluator import Evaluator
from src.visualization.plots import create_all_plots
from src.data.dataset import SignalDataset


def get_device(device_str: str = 'auto') -> torch.device:
    """
    Get the appropriate device for training.
    
    Args:
        device_str: Device string ('cpu', 'cuda', 'mps', or 'auto')
    
    Returns:
        torch.device object
    """
    if device_str == 'auto':
        # Auto-detect best available device
        if torch.cuda.is_available():
            return torch.device('cuda')
        elif torch.backends.mps.is_available():
            return torch.device('mps')
        else:
            return torch.device('cpu')
    elif device_str == 'cuda':
        if torch.cuda.is_available():
            return torch.device('cuda')
        else:
            print("Warning: CUDA requested but not available. Falling back to CPU.")
            return torch.device('cpu')
    elif device_str == 'mps':
        if torch.backends.mps.is_available():
            return torch.device('mps')
        else:
            print("Warning: MPS requested but not available. Falling back to CPU.")
            return torch.device('cpu')
    else:
        return torch.device('cpu')


def main(
    frequencies: list = [1.0, 3.0, 5.0, 7.0],
    sampling_rate: float = 1000.0,
    duration: float = 10.0,
    train_seed: int = 1,
    test_seed: int = 2,
    hidden_size: int = 128,
    num_layers: int = 1,
    learning_rate: float = 0.0005,
    num_epochs: int = 50,
    batch_size: int = 1,
    sequence_length: int = 50,
    reset_state: bool = True,
    device: str = 'cpu',
    output_dir: str = 'outputs'
):
    """
    Main training and evaluation pipeline.
    
    Args:
        frequencies: List of 4 frequencies in Hz
        sampling_rate: Sampling rate in Hz
        duration: Signal duration in seconds
        train_seed: Random seed for training set
        test_seed: Random seed for test set
        hidden_size: LSTM hidden state size
        num_layers: Number of LSTM layers
        learning_rate: Learning rate for optimizer
        num_epochs: Number of training epochs
        batch_size: Batch size for training
        sequence_length: Length of input sequences (L). Default is 50.
        reset_state: Whether to reset LSTM state between samples
        device: Device to use ('auto', 'cpu', 'cuda', or 'mps')
        output_dir: Directory to save outputs
    """
    print("=" * 60)
    print("LSTM Signal Extraction - Training Pipeline")
    print("=" * 60)
    
    # Set device
    device_obj = get_device(device)
    if device_obj.type == 'cuda':
        print(f"Using device: CUDA ({torch.cuda.get_device_name(0)})")
    elif device_obj.type == 'mps':
        print(f"Using device: MPS (Metal Performance Shaders)")
    else:
        print(f"Using device: CPU")
    
    device = device_obj
    
    # Create output directories
    model_dir = os.path.join(output_dir, 'models')
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    # Create data directory
    data_dir = os.path.join(output_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    train_data_path = os.path.join(data_dir, 'train_dataset.pkl')
    test_data_path = os.path.join(data_dir, 'test_dataset.pkl')
    
    # Step 1: Generate or load datasets
    print("\n[1/6] Generating/loading datasets...")
    train_loader, test_loader = create_dataloaders(
        train_seed=train_seed,
        test_seed=test_seed,
        frequencies=frequencies,
        sampling_rate=sampling_rate,
        duration=duration,
        batch_size=batch_size,
        sequence_length=sequence_length,
        shuffle=False,
        train_data_path=train_data_path if os.path.exists(train_data_path) else None,
        test_data_path=test_data_path if os.path.exists(test_data_path) else None
    )
    
    print(f"  Training samples: {len(train_loader.dataset)}")
    print(f"  Test samples: {len(test_loader.dataset)}")
    
    # Save datasets if they don't exist
    if not os.path.exists(train_data_path) or not os.path.exists(test_data_path):
        print("\n  Generating and saving datasets...")
        train_dataset_gen = SignalDataset(seed=train_seed, frequencies=frequencies, 
                                         sampling_rate=sampling_rate, duration=duration)
        train_inputs, train_targets = train_dataset_gen.generate_dataset(sequence_length=sequence_length)
        train_dataset_gen.save_dataset(train_data_path, train_inputs, train_targets)
        
        test_dataset_gen = SignalDataset(seed=test_seed, frequencies=frequencies,
                                       sampling_rate=sampling_rate, duration=duration)
        test_inputs, test_targets = test_dataset_gen.generate_dataset(sequence_length=sequence_length)
        test_dataset_gen.save_dataset(test_data_path, test_inputs, test_targets)
    
    # Step 2: Create model
    print("\n[2/6] Creating LSTM model...")
    model = ConditionalLSTM(
        input_size=5,  # 1 signal + 4 one-hot selector
        hidden_size=hidden_size,
        num_layers=num_layers
    )
    model.to(device)
    print(f"  Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Step 3: Train model
    print("\n[3/6] Training model...")
    trainer = Trainer(model, learning_rate=learning_rate, device=device)
    history = trainer.train(
        train_loader,
        num_epochs=num_epochs,
        reset_state=reset_state,
        verbose=True
    )
    
    # Calculate final MSE_train
    mse_train = trainer.calculate_mse(train_loader, reset_state=reset_state)
    print(f"\n  Final MSE_train: {mse_train:.6f}")
    
    # Step 4: Evaluate on test set
    print("\n[4/6] Evaluating on test set...")
    evaluator = Evaluator(model, device=device)
    eval_results = evaluator.evaluate(test_loader, reset_state=reset_state)
    mse_test = eval_results['mse_test']
    print(f"  MSE_test: {mse_test:.6f}")
    
    # Step 5: Check generalization
    print("\n[5/6] Checking generalization...")
    gen_results = evaluator.check_generalization(mse_train, mse_test)
    print(f"  Relative difference: {gen_results['relative_difference']:.4f}")
    if gen_results['generalizes_well']:
        print("  ✓ Model generalizes well!")
    else:
        print("  ✗ Model may be overfitting")
    
    # Step 6: Generate predictions for visualization
    print("\n[6/6] Generating predictions for visualization...")
    
    # Generate test dataset to get mixed signal and targets
    test_dataset_gen = SignalDataset(
        seed=test_seed,
        frequencies=frequencies,
        sampling_rate=sampling_rate,
        duration=duration
    )
    test_mixed_signal = test_dataset_gen.generate_mixed_signal(normalize=True)
    test_time = test_dataset_gen.t
    
    # Generate pure targets
    test_targets = []
    for freq in frequencies:
        target = test_dataset_gen.generate_pure_target(freq)
        test_targets.append(target)
    test_targets = np.array(test_targets)  # Shape: (4, num_samples)
    
    # Generate predictions for all frequencies
    test_predictions = evaluator.predict_all_frequencies(
        test_mixed_signal,
        reset_state=reset_state
    )
    
    # Step 7: Create visualizations
    print("\n[7/6] Creating visualizations...")
    create_all_plots(
        targets=test_targets,
        predictions=test_predictions,
        mixed_signal=test_mixed_signal,
        time=test_time,
        frequencies=frequencies,
        history=history,
        mse_train=mse_train,
        mse_test=mse_test,
        output_dir=plots_dir
    )
    
    # Step 8: Save model
    print("\n[8/6] Saving model...")
    model_path = os.path.join(model_dir, 'lstm_model.pt')
    trainer.save_model(model_path)
    print(f"  Model saved to {model_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"MSE_train: {mse_train:.6f}")
    print(f"MSE_test: {mse_test:.6f}")
    print(f"Generalization: {'Good' if gen_results['generalizes_well'] else 'Poor'}")
    print(f"\nOutputs saved to: {output_dir}")
    print(f"  - Model: {model_dir}")
    print(f"  - Plots: {plots_dir}")
    print(f"  - Data: {data_dir}")
    print("=" * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train LSTM for signal extraction')
    parser.add_argument('--frequencies', type=float, nargs=4, default=[1.0, 3.0, 5.0, 7.0],
                        help='Frequencies in Hz (default: 1.0 3.0 5.0 7.0)')
    parser.add_argument('--sampling-rate', type=float, default=1000.0,
                        help='Sampling rate in Hz (default: 1000.0)')
    parser.add_argument('--duration', type=float, default=10.0,
                        help='Signal duration in seconds (default: 10.0)')
    parser.add_argument('--train-seed', type=int, default=1,
                        help='Random seed for training set (default: 1)')
    parser.add_argument('--test-seed', type=int, default=2,
                        help='Random seed for test set (default: 2)')
    parser.add_argument('--hidden-size', type=int, default=128,
                        help='LSTM hidden state size (default: 128)')
    parser.add_argument('--num-layers', type=int, default=1,
                        help='Number of LSTM layers (default: 1)')
    parser.add_argument('--learning-rate', type=float, default=0.0005,
                        help='Learning rate (default: 0.0005)')
    parser.add_argument('--num-epochs', type=int, default=50,
                        help='Number of training epochs (default: 50)')
    parser.add_argument('--batch-size', type=int, default=1,
                        help='Batch size (default: 1)')
    parser.add_argument('--sequence-length', type=int, default=50,
                        help='Sequence length (L) for LSTM input (default: 50)')
    parser.add_argument('--reset-state', action='store_true', default=True,
                        help='Reset LSTM state between samples (default: True)')
    parser.add_argument('--device', type=str, default='auto',
                        choices=['auto', 'cpu', 'cuda', 'mps'],
                        help='Device to use: auto (detect best), cpu, cuda, or mps (default: auto)')
    parser.add_argument('--output-dir', type=str, default='outputs',
                        help='Output directory (default: outputs)')
    
    args = parser.parse_args()
    
    main(
        frequencies=args.frequencies,
        sampling_rate=args.sampling_rate,
        duration=args.duration,
        train_seed=args.train_seed,
        test_seed=args.test_seed,
        hidden_size=args.hidden_size,
        num_layers=args.num_layers,
        learning_rate=args.learning_rate,
        num_epochs=args.num_epochs,
        batch_size=args.batch_size,
        sequence_length=args.sequence_length,
        reset_state=args.reset_state,
        device=args.device,
        output_dir=args.output_dir
    )

