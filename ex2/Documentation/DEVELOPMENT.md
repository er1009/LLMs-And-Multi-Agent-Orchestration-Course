# Development Documentation

This document tracks the development process, decisions, challenges, and solutions for the LSTM Signal Extraction project.

## Development Process

### Phase 1: Project Setup

**Decisions:**
- Used PyTorch for LSTM implementation (better control over state management)
- Organized code into modular structure: data, model, training, evaluation, visualization
- Followed same directory structure as ex1 for consistency

**Challenges:**
- Understanding the critical requirement for state reset in L=1 sequence length
- Ensuring proper one-hot encoding in dataset generation

**Solutions:**
- Implemented explicit state reset functionality in LSTM model
- Created clear dataset structure with [S[t], C1, C2, C3, C4] input format

### Phase 2: Dataset Generation

**Decisions:**
- Implemented noisy signal generation with amplitude and phase noise at each sample
- Used separate random seeds for train/test sets to ensure different noise realizations
- Created 40,000 samples (10,000 time points × 4 frequencies)

**Challenges:**
- Ensuring noise varies at every sample (not just per frequency)
- Proper normalization of mixed signal

**Solutions:**
- Generated random amplitude and phase for each sample independently
- Normalized mixed signal by dividing by 4 (number of frequencies)

### Phase 3: LSTM Model Implementation

**Decisions:**
- Used single-layer LSTM with configurable hidden size
- Implemented explicit state reset functionality
- Added forward pass with optional hidden state management

**Challenges:**
- Understanding the critical requirement for state reset in L=1
- Proper handling of batch dimensions in forward pass

**Solutions:**
- Implemented `reset_state()` method that creates zero-initialized hidden states
- Ensured state is reset between samples in training loop
- Added proper dimension handling for sequence length L=1

### Phase 4: Training Implementation

**Decisions:**
- Used MSE loss function (as specified in requirements)
- Implemented Adam optimizer with configurable learning rate
- Added state reset in training loop (critical for L=1)

**Challenges:**
- Ensuring state is reset correctly between samples
- Calculating MSE_train correctly

**Solutions:**
- Reset state before each sample in training loop
- Implemented separate MSE calculation function for evaluation

### Phase 5: Evaluation and Generalization

**Decisions:**
- Implemented separate evaluation module for test set
- Added generalization checking with relative difference calculation
- Created prediction function for all frequencies

**Challenges:**
- Ensuring test set uses different seed (different noise)
- Calculating MSE_test correctly

**Solutions:**
- Used seed #2 for test set (seed #1 for training)
- Implemented same MSE calculation for test set as training set

### Phase 6: Visualization

**Decisions:**
- Created plots for single frequency comparison
- Generated plots for all 4 frequencies
- Added training history and MSE comparison plots

**Challenges:**
- Ensuring plots match homework requirements
- Proper visualization of predictions vs targets

**Solutions:**
- Implemented plots showing Target, LSTM Output (points), and S (mixed noisy input)
- Created subplot structure for all 4 frequencies

## Key Technical Decisions

### 1. State Management Implementation

**Decision:** Do NOT reset LSTM state between consecutive samples for L=1 sequence length.

**Rationale:** The homework explicitly requires that state should NOT be reset between consecutive samples. State is passed from one sample to the next to allow temporal dependency learning. This is critical for the exercise.

**Implementation:**
```python
# Initialize state at start of epoch
hidden_state = model.reset_state(batch_size=1, device=device)
# Pass state from one sample to the next (do NOT reset between samples)
output, hidden_state = model(input, hidden_state)
```

### 2. Dataset Structure

**Decision:** Create 40,000 samples (10,000 time points × 4 frequencies) with one-hot encoded frequency selector.

**Rationale:** This structure allows the model to learn which frequency to extract based on the conditional input.

**Implementation:**
```python
# Input: [S[t], C1, C2, C3, C4]
# Target: Target_i[t]
```

### 3. Noise Generation

**Decision:** Generate random amplitude and phase for each sample independently.

**Rationale:** The homework requires noise to vary at every sample, not just per frequency.

**Implementation:**
```python
amplitudes = np.random.uniform(0.8, 1.2, num_samples)
phases = np.random.uniform(0, 2 * np.pi, num_samples)
```

### 4. Train/Test Split

**Decision:** Use different random seeds for train and test sets.

**Rationale:** This ensures different noise realizations for generalization testing.

**Implementation:**
```python
train_dataset = SignalDataset(seed=1)
test_dataset = SignalDataset(seed=2)
```

## Challenges Encountered

### Challenge 1: Understanding State Management Requirement

**Problem:** Initially unclear how state should be managed for L=1.

**Solution:** The homework explicitly states that state should NOT be reset between consecutive samples for L=1. State is passed from one sample to the next to allow temporal dependency learning. This allows the network to learn sequential patterns by actively managing state across the sequence.

### Challenge 2: Proper One-Hot Encoding

**Problem:** Ensuring one-hot encoding is correct in dataset generation.

**Solution:** Implemented explicit one-hot encoding with exactly one 1 per sample.

### Challenge 3: MSE Calculation

**Problem:** Ensuring MSE is calculated correctly for both training and test sets.

**Solution:** Implemented separate MSE calculation function that can be used for both sets.

## Lessons Learned

1. **State Management is Critical:** The requirement to NOT reset state between consecutive samples for L=1 is not intuitive but is critical for the exercise. State must be passed from one sample to the next to allow temporal dependency learning.

2. **Dataset Structure Matters:** The one-hot encoded frequency selector is essential for conditional regression.

3. **Noise Variation:** Ensuring noise varies at every sample (not just per frequency) is important for the problem.

4. **Generalization Testing:** Using different seeds for train/test sets ensures proper generalization evaluation.

5. **Modular Design:** Organizing code into modules (data, model, training, evaluation, visualization) makes the codebase maintainable.

## Future Improvements

1. **Sequence Length L>1:** Implement sliding window approach for longer sequences (as suggested in homework).

2. **Hyperparameter Tuning:** Add hyperparameter tuning for learning rate, hidden size, etc.

3. **Model Architecture:** Experiment with different LSTM architectures (multi-layer, bidirectional).

4. **Visualization:** Add more detailed visualizations (frequency domain analysis, etc.).

5. **Documentation:** Add more detailed code comments and docstrings.

