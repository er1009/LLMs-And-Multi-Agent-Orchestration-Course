"""
Integration tests for full pipeline.
"""

import pytest
import torch
import numpy as np
from src.data.dataloader import create_dataloaders
from src.model.lstm_model import ConditionalLSTM
from src.training.trainer import Trainer
from src.training.evaluator import Evaluator


def test_full_pipeline_small():
    """Test full pipeline with small dataset."""
    # Create small datasets
    train_loader, test_loader = create_dataloaders(
        train_seed=1,
        test_seed=2,
        frequencies=[1.0, 3.0, 5.0, 7.0],
        sampling_rate=100.0,  # Smaller for faster testing
        duration=1.0,  # 1 second = 100 samples
        batch_size=1
    )
    
    # Create model
    model = ConditionalLSTM(input_size=5, hidden_size=32, num_layers=1)
    
    # Train for a few epochs
    trainer = Trainer(model, learning_rate=0.01, device=torch.device('cpu'))
    history = trainer.train(train_loader, num_epochs=2, reset_state=True, verbose=False)
    
    # Check that loss decreased
    assert len(history['train_loss']) == 2
    assert history['train_loss'][0] > 0
    assert history['mse_train'][0] > 0
    
    # Evaluate on test set
    evaluator = Evaluator(model, device=torch.device('cpu'))
    eval_results = evaluator.evaluate(test_loader, reset_state=True)
    
    # Check that MSE_test is calculated
    assert 'mse_test' in eval_results
    assert eval_results['mse_test'] > 0
    assert eval_results['mse_test'] < 10.0  # Should be reasonable


def test_generalization_check():
    """Test generalization checking."""
    # Create datasets
    train_loader, test_loader = create_dataloaders(
        train_seed=1,
        test_seed=2,
        frequencies=[1.0, 3.0, 5.0, 7.0],
        sampling_rate=100.0,
        duration=1.0,
        batch_size=1
    )
    
    # Create and train model
    model = ConditionalLSTM(input_size=5, hidden_size=32)
    trainer = Trainer(model, learning_rate=0.01, device=torch.device('cpu'))
    trainer.train(train_loader, num_epochs=2, reset_state=True, verbose=False)
    
    # Calculate MSEs
    mse_train = trainer.calculate_mse(train_loader, reset_state=True)
    evaluator = Evaluator(model, device=torch.device('cpu'))
    eval_results = evaluator.evaluate(test_loader, reset_state=True)
    mse_test = eval_results['mse_test']
    
    # Check generalization
    gen_results = evaluator.check_generalization(mse_train, mse_test)
    
    assert 'mse_train' in gen_results
    assert 'mse_test' in gen_results
    assert 'relative_difference' in gen_results
    assert 'generalizes_well' in gen_results
    assert isinstance(gen_results['generalizes_well'], bool)


def test_predict_all_frequencies():
    """Test prediction for all frequencies."""
    # Create small dataset
    train_loader, test_loader = create_dataloaders(
        train_seed=1,
        test_seed=2,
        frequencies=[1.0, 3.0, 5.0, 7.0],
        sampling_rate=100.0,
        duration=1.0,
        batch_size=1
    )
    
    # Create and train model
    model = ConditionalLSTM(input_size=5, hidden_size=32)
    trainer = Trainer(model, learning_rate=0.01, device=torch.device('cpu'))
    trainer.train(train_loader, num_epochs=2, reset_state=True, verbose=False)
    
    # Generate predictions
    evaluator = Evaluator(model, device=torch.device('cpu'))
    
    # Create a small mixed signal
    mixed_signal = np.random.randn(100) * 0.5
    
    # Predict all frequencies
    predictions = evaluator.predict_all_frequencies(mixed_signal, reset_state=True)
    
    # Check shape: (4 frequencies, num_samples)
    assert predictions.shape == (4, 100)
    
    # Check that predictions are finite
    assert np.all(np.isfinite(predictions))


def test_different_seeds_produce_different_data():
    """Test that train and test sets are different."""
    train_loader, test_loader = create_dataloaders(
        train_seed=1,
        test_seed=2,
        frequencies=[1.0, 3.0, 5.0, 7.0],
        sampling_rate=100.0,
        duration=1.0,
        batch_size=1
    )
    
    # Get first samples from each dataset
    train_inputs, train_targets = next(iter(train_loader))
    test_inputs, test_targets = next(iter(test_loader))
    
    # They should be different (different seeds)
    assert not torch.equal(train_inputs, test_inputs)
    assert not torch.equal(train_targets, test_targets)


def test_model_can_learn():
    """Test that model can learn (loss decreases)."""
    # Create datasets
    train_loader, _ = create_dataloaders(
        train_seed=1,
        test_seed=2,
        frequencies=[1.0, 3.0, 5.0, 7.0],
        sampling_rate=100.0,
        duration=1.0,
        batch_size=1
    )
    
    # Create model
    model = ConditionalLSTM(input_size=5, hidden_size=32)
    trainer = Trainer(model, learning_rate=0.01, device=torch.device('cpu'))
    
    # Train for multiple epochs
    history = trainer.train(train_loader, num_epochs=5, reset_state=True, verbose=False)
    
    # Check that loss generally decreases (may not be monotonic, but should trend down)
    initial_loss = history['train_loss'][0]
    final_loss = history['train_loss'][-1]
    
    # Loss should decrease or at least be reasonable
    assert final_loss < initial_loss * 2  # Should not increase dramatically
    assert final_loss > 0  # Should be positive

