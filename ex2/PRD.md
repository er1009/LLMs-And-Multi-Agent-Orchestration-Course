# LSTM Signal Extraction - Product Requirements Document (PRD)

## 1. Project Overview

### 1.1 Objective
Build a PyTorch-based LSTM neural network that performs conditional regression to extract individual frequency components from mixed noisy signals. The system uses a one-hot encoded frequency selector to determine which frequency component to extract from the mixed signal.

### 1.2 Key Goals
- Demonstrate proficiency in LSTM architecture and state management
- Implement conditional regression for signal extraction
- Create a complete ML pipeline: data generation → training → evaluation → visualization
- Document the development process professionally

### 1.3 Project Purpose & Motivation
This project serves as an educational exercise to understand:
- LSTM neural network architecture and state management
- Conditional regression for signal processing
- Complete machine learning pipeline development
- Professional software engineering practices for ML projects

### 1.4 Market / Domain Context
**Domain:** Signal Processing, Deep Learning, Time Series Analysis

**Applications:**
- Audio signal separation (e.g., separating instruments in music)
- Biomedical signal processing (e.g., EEG, ECG analysis)
- Communication systems (e.g., frequency division multiplexing)
- Sensor data analysis (e.g., extracting specific frequency components from noisy sensor readings)

**Research Context:**
- Demonstrates conditional learning in recurrent neural networks
- Explores state management in sequence-to-sequence models
- Validates generalization in synthetic signal processing tasks

### 1.5 Stakeholders & Personas

**Primary Stakeholders:**
1. **Student/Developer (Primary User)**
   - **Role:** Implements and runs the system
   - **Needs:** Clear documentation, working code, educational value
   - **Goals:** Learn LSTM architecture, complete assignment

2. **Instructor/Evaluator (Secondary User)**
   - **Role:** Reviews and grades the project
   - **Needs:** Complete documentation, reproducible results, code quality
   - **Goals:** Assess understanding of LSTM concepts and software engineering practices

3. **Future Maintainers (Tertiary User)**
   - **Role:** May extend or modify the codebase
   - **Needs:** Well-documented, modular code structure
   - **Goals:** Understand and extend functionality

## 2. Problem Statement

### 2.1 The Problem
Given a mixed and noisy signal `S(t)` composed of four different sinusoidal frequencies with random amplitude and phase noise at each sample, develop an LSTM network capable of extracting each pure frequency component separately while completely ignoring the noise.

### 2.2 The Principle
The system performs **Conditional Regression** (רגרסיה מותנית):
- **Input:** `(S[t], C)` where:
  - `S[t]`: A sample from the noisy signal
  - `C`: A One-Hot encoded vector for frequency selection `[C1, C2, C3, C4]`
- **Target Output:** `Target_i[t]`: The pure target frequency `i` at time `t`

### 2.3 Usage Example
If the choice vector `C` is `[0, 1, 0, 0]`, the goal is to extract the pure frequency `f2`. The system processes:
- `(S[0] (noisy) + C) -> LSTM -> Sinus_2^pure[0] (pure)`
- `(S[1] (noisy) + C) -> LSTM -> Sinus_2^pure[1] (pure)`

## 3. Functional Requirements

### 3.1 User Stories

**As a developer/researcher, I want to:**
1. Generate synthetic signal datasets with configurable parameters
2. Train an LSTM model to extract frequency components
3. Evaluate model performance on test data
4. Visualize predictions and compare with ground truth
5. Reproduce experiments with saved datasets

**As an evaluator, I want to:**
1. Run the complete pipeline with default parameters
2. Verify that tests pass and produce expected results
3. Review code quality and documentation
4. Understand the architecture and design decisions

### 3.2 Use Cases

**UC1: Generate Training Dataset**
- **Actor:** Developer
- **Precondition:** Python environment set up
- **Flow:**
  1. Configure frequencies, sampling rate, duration
  2. Set random seed for training set
  3. Generate 40,000 samples (10,000 time points × 4 frequencies)
  4. Save dataset to disk (optional)
- **Postcondition:** Training dataset ready for use

**UC2: Train LSTM Model**
- **Actor:** Developer
- **Precondition:** Training dataset available
- **Flow:**
  1. Initialize LSTM model with configurable parameters
  2. Train for N epochs with state management
  3. Track training loss and MSE_train
  4. Save model checkpoint
- **Postcondition:** Trained model available

**UC3: Evaluate Model**
- **Actor:** Developer
- **Precondition:** Trained model available
- **Flow:**
  1. Load test dataset (different seed)
  2. Evaluate model on test set
  3. Calculate MSE_test
  4. Check generalization (compare MSE_train vs MSE_test)
- **Postcondition:** Evaluation metrics available

**UC4: Generate Visualizations**
- **Actor:** Developer
- **Precondition:** Trained model and test predictions available
- **Flow:**
  1. Generate predictions for all frequencies
  2. Create comparison plots
  3. Save plots to disk
- **Postcondition:** Visualization files created

### 3.3 System Requirements

**SR1: Data Generation**
- System must generate synthetic signals with configurable frequencies
- System must support different random seeds for train/test sets
- System must create datasets with correct input/output shapes

**SR2: Model Training**
- System must support configurable LSTM architecture (hidden size, layers)
- System must manage LSTM state correctly (not reset between consecutive samples)
- System must track training metrics (loss, MSE)

**SR3: Model Evaluation**
- System must calculate MSE on both training and test sets
- System must check generalization (compare train vs test MSE)
- System must generate predictions for visualization

**SR4: Visualization**
- System must create comparison plots (target vs prediction)
- System must generate training history plots
- System must save all plots to disk

## 4. Non-Functional Requirements

### 4.1 Performance
- **Training Time:** Should complete 10 epochs in reasonable time (< 1 hour on CPU)
- **Memory Usage:** Should run on systems with ≥ 4GB RAM
- **Device Support:** Must support CPU, CUDA (NVIDIA GPU), and MPS (Apple Silicon)

### 4.2 Scalability
- **Dataset Size:** Configurable via parameters (duration, sampling rate)
- **Model Size:** Configurable hidden size and number of layers
- **Current Limitation:** Single-machine execution (no distributed training)

### 4.3 Reliability
- **Reproducibility:** Results must be reproducible with same random seeds
- **Error Handling:** Graceful handling of device unavailability (fallback to CPU)
- **Data Persistence:** Optional dataset caching to avoid regeneration

### 4.4 Usability
- **Command-Line Interface:** Simple CLI with clear argument descriptions
- **Documentation:** Comprehensive README with installation and usage instructions
- **Error Messages:** Clear, actionable error messages

### 4.5 Security
- **No External Dependencies:** All data is synthetically generated (no external data sources)
- **No Network Access:** No external API calls or network dependencies
- **Local Execution:** All processing happens locally

### 4.6 Maintainability
- **Modular Design:** Clear separation of concerns (data, model, training, evaluation)
- **Code Quality:** Follows single responsibility principle, DRY principles
- **Documentation:** Comprehensive docstrings and comments

### 4.7 Portability
- **Cross-Platform:** Works on macOS, Linux, Windows
- **Python Version:** Supports Python 3.8+
- **Dependency Management:** Uses requirements.txt for dependency specification

## 5. Constraints

### 5.1 Technical Constraints
- **Framework:** Must use PyTorch for LSTM implementation
- **Python Version:** Minimum Python 3.8
- **Sequence Length:** Primary focus on L=1 (individual samples)
- **Batch Size:** Must support batch_size=1 for L=1

### 5.2 Legal/Ethical Constraints
- **No Real Data:** Uses only synthetic data (no privacy concerns)
- **Academic Use:** Intended for educational purposes

### 5.3 Budget Constraints
- **No Cloud Resources:** Must run on local hardware
- **No Paid Services:** Uses only open-source libraries

### 5.4 Timeline Constraints
- **Academic Assignment:** Must be completed within course timeline
- **Deliverables:** Must include code, tests, documentation, and results

## 6. Acceptance Criteria / KPIs

### 6.1 Functional Acceptance Criteria
- ✅ Dataset generation produces correct shapes (40,000 samples, input shape (5,), target shape ())
- ✅ LSTM model processes inputs and produces valid outputs
- ✅ Training loop decreases loss over epochs
- ✅ MSE_train and MSE_test are calculated correctly
- ✅ Model generalizes well (MSE_test ≈ MSE_train, relative difference < 10%)
- ✅ Visualizations are generated correctly (4 plots as specified)
- ✅ All unit tests pass
- ✅ Integration tests pass

### 6.2 Non-Functional Acceptance Criteria
- ✅ Code follows modular structure
- ✅ All modules have docstrings
- ✅ README is complete and clear
- ✅ Architecture document exists
- ✅ Tests have ≥70% coverage for core logic
- ✅ No hardcoded secrets or credentials

### 6.3 Success Metrics
- **MSE_train:** Should decrease over training epochs
- **MSE_test:** Should be close to MSE_train (generalization)
- **Test Coverage:** ≥70% for core modules
- **Documentation:** All required documents present and complete

## 7. In-Scope / Out-of-Scope

### 7.1 In-Scope
- Synthetic signal generation with configurable parameters
- LSTM model implementation with state management
- Training pipeline with MSE tracking
- Test set evaluation and generalization checking
- Visualization generation (4 required plots)
- Unit and integration tests
- Complete documentation (PRD, Architecture, README, Development notes)

### 7.2 Out-of-Scope
- Real-world signal data processing
- Hyperparameter tuning automation
- Distributed training (multi-GPU)
- Model serving API
- Interactive visualization dashboard
- Production deployment
- Model compression or quantization

## 8. Deliverables

1. **Source Code**
   - Complete implementation in `src/` directory
   - Modular structure (data, model, training, evaluation, visualization)

2. **Tests**
   - Unit tests in `tests/` directory
   - Integration tests
   - Test coverage report

3. **Documentation**
   - README.md (installation, usage, troubleshooting)
   - PRD.md (this document)
   - ARCHITECTURE.md (system architecture)
   - Documentation/ folder (development process, AI prompts)

4. **Results**
   - Trained model checkpoint
   - Generated visualizations
   - Training metrics (MSE_train, MSE_test)

5. **Configuration**
   - requirements.txt (dependencies)
   - .gitignore (version control)

## 9. Timeline & Milestones

### Milestone 1: Project Setup
- Create project structure
- Set up development environment
- Create PRD and Architecture documents

### Milestone 2: Data Generation
- Implement SignalDataset class
- Generate train/test datasets
- Create unit tests for data generation

### Milestone 3: Model Implementation
- Implement ConditionalLSTM class
- Implement state management
- Create unit tests for model

### Milestone 4: Training Pipeline
- Implement Trainer class
- Implement training loop with state management
- Track training metrics

### Milestone 5: Evaluation
- Implement Evaluator class
- Calculate MSE_train and MSE_test
- Check generalization

### Milestone 6: Visualization
- Implement plotting functions
- Generate all required plots
- Save plots to disk

### Milestone 7: Testing & Documentation
- Complete unit and integration tests
- Write comprehensive README
- Finalize all documentation

## 10. Technical Requirements

### 10.1 Dataset Generation

#### 3.1.1 General Parameters
- **Frequencies:** `f1 = 1 Hz`, `f2 = 3 Hz`, `f3 = 5 Hz`, `f4 = 7 Hz`
- **Time range:** `0 - 10` seconds
- **Sampling rate:** `Fs = 1000 Hz`
- **Total samples:** `10,000` time points

#### 3.1.2 Noisy Signal Creation (S)
For each frequency `i` and sample `t`:
- **Amplitude:** `A_i(t) ~ Uniform(0.8, 1.2)` (varies at each sample)
- **Phase:** `φ_i(t) ~ Uniform(0, 2π)` (varies at each sample)
- **Noisy Sine Wave:** `Sinus_i^noisy(t) = A_i(t) · sin(2π · f_i · t + φ_i(t))`
- **Mixed Signal:** `S(t) = (1/4) · Σ_{i=1}^{4} Sinus_i^noisy(t)`

#### 3.1.3 Ground Truth Targets
- **Pure Target:** `Target_i(t) = sin(2π · f_i · t)` (noiseless)

#### 3.1.4 Train vs. Test Sets
- **Training Set:** Uses random seed #1
- **Test Set:** Uses random seed #2 (same frequencies, completely different noise)

#### 3.1.5 Dataset Structure
- **Total Rows:** 40,000 (10,000 samples × 4 frequencies)
- **Input Vector:** `[S[t], C1, C2, C3, C4]` (size 5)
- **Output:** `Target_i[t]` (scalar)

### 3.2 LSTM Model Architecture

#### 3.2.1 Model Specifications
- **Input dimension:** 5 (1 signal value + 4 one-hot frequency selector)
- **Output dimension:** 1 (predicted target value)
- **Sequence length:** `L = 1` (each sample processed independently)
- **Hidden size:** Configurable (default: 64)
- **Number of layers:** Configurable (default: 1)

#### 3.2.2 Critical Implementation Requirements (L = 1)
- **State Management:** The internal state (`h_t`, `c_t`) must **NOT be reset** between consecutive samples
- **Rationale:** This allows the network to learn temporal dependency by passing state from one sample to the next
- **Implementation:** State is initialized at the start of epoch, then passed from one sample to the next in the training loop

### 3.3 Training Requirements

#### 3.3.1 Training Configuration
- **Loss function:** Mean Squared Error (MSE)
- **Optimizer:** Adam
- **Learning rate:** Configurable (default: 0.001)
- **Number of epochs:** Configurable (default: 10)
- **Batch size:** 1 (for L=1 sequence length)

#### 3.3.2 Metrics
- **MSE_train:** `(1/40000) · Σ_{j=1}^{40000} (LSTM(S_train[t], C) - Target[t])^2`
- **MSE_test:** `(1/40000) · Σ_{j=1}^{40000} (LSTM(S_test[t], C) - Target[t])^2`

### 3.4 Evaluation Requirements

#### 3.4.1 Success Metrics
1. **MSE on training set:** Calculate and report MSE_train
2. **MSE on test set:** Calculate and report MSE_test
3. **Generalization:** If `MSE_test ≈ MSE_train`, the system generalizes well

#### 3.4.2 Visualization Requirements
1. **Graph 1:** Comparison to a single frequency (e.g., f2)
   - Display: `Target_2`, `LSTM Output` (points), `S` (mixed noisy input)
2. **Graph 2:** All 4 extracted frequencies
   - 4 sub-graphs, each showing extraction of one frequency component

## 11. Project Structure

```
ex2/
├── README.md                 # Main documentation
├── PRD.md                    # This specification document
├── requirements.txt          # Python dependencies
├── src/                      # Source code
│   ├── __init__.py
│   ├── main.py              # Entry point for training
│   ├── data/
│   │   ├── __init__.py
│   │   ├── dataset.py       # Dataset generation
│   │   └── dataloader.py    # PyTorch DataLoader wrapper
│   ├── model/
│   │   ├── __init__.py
│   │   └── lstm_model.py    # LSTM architecture
│   ├── training/
│   │   ├── __init__.py
│   │   ├── trainer.py       # Training loop
│   │   └── evaluator.py     # Evaluation and generalization
│   └── visualization/
│       ├── __init__.py
│       └── plots.py         # Graph generation
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_dataset.py      # Test data generation
│   ├── test_model.py        # Test LSTM model
│   └── test_integration.py  # End-to-end tests
├── Documentation/            # Development documentation
│   ├── PRD_PROMPT.md        # Initial prompt for PRD
│   ├── DEVELOPMENT.md       # Development process notes
│   └── AI_PROMPTS.md        # AI prompting documentation
└── outputs/
    ├── models/              # Saved model checkpoints
    └── plots/               # Generated graphs
```

## 12. Implementation Details

### 5.1 Dataset Generation Module
**Responsibilities:**
- Generate noisy signals for each frequency
- Create mixed signal S(t)
- Generate pure targets
- Create train/test datasets with different seeds

**Key Functions:**
- `generate_noisy_signal(frequency: float) -> np.ndarray`
- `generate_mixed_signal() -> np.ndarray`
- `generate_pure_target(frequency: float) -> np.ndarray`
- `generate_dataset() -> Tuple[np.ndarray, np.ndarray]`

### 5.2 LSTM Model Module
**Responsibilities:**
- Define LSTM architecture
- Handle state reset functionality
- Forward pass with conditional input

**Key Functions:**
- `forward(x, hidden_state) -> (output, hidden_state)`
- `reset_state(batch_size, device) -> (h_0, c_0)`
- `predict_single(x, reset_state) -> output`

### 5.3 Training Module
**Responsibilities:**
- Training loop with state management
- MSE calculation
- Model checkpointing

**Key Functions:**
- `train_epoch(train_loader, reset_state) -> metrics`
- `train(num_epochs) -> history`
- `calculate_mse(data_loader) -> float`

### 5.4 Evaluation Module
**Responsibilities:**
- Test set evaluation
- Generalization checking
- Prediction generation

**Key Functions:**
- `evaluate(test_loader) -> metrics`
- `check_generalization(mse_train, mse_test) -> results`
- `predict_all_frequencies(mixed_signal) -> predictions`

### 5.5 Visualization Module
**Responsibilities:**
- Generate comparison graphs
- Plot training history
- Create MSE comparison plots

**Key Functions:**
- `plot_single_frequency_comparison(...)`
- `plot_all_frequencies(...)`
- `plot_training_history(...)`
- `plot_mse_comparison(...)`

## 13. Testing Requirements

### 6.1 Unit Tests
Must include tests for:
- Dataset generation (correct shapes, value ranges, seed reproducibility)
- LSTM model (forward pass, state reset, input/output dimensions)
- Training loop (loss calculation, state management)
- Evaluation (MSE calculation, generalization check)

### 6.2 Integration Tests
- End-to-end pipeline: data generation → training → evaluation
- Model can learn (loss decreases)
- Predictions are generated correctly
- Train and test sets are different

## 14. Documentation Requirements

### 7.1 README.md
Must include:
1. **Project Title and Description**
2. **Installation Instructions:**
   - Prerequisites (Python version, PyTorch installation)
   - Virtual environment setup
   - Dependency installation
3. **Usage Instructions:**
   - How to run training
   - Command-line arguments
   - Expected outputs
4. **Testing:**
   - How to run tests
   - Expected test results
5. **Project Structure:** Brief overview of directories
6. **Results:** Expected MSE values and generalization status

### 7.2 Documentation Folder
Must contain:
1. **PRD_PROMPT.md:** The initial prompt used to generate this PRD
2. **DEVELOPMENT.md:** Development process, decisions, challenges
3. **AI_PROMPTS.md:**
   - All prompts used with AI assistants
   - Prompt iterations and refinements
   - What worked and what didn't

## 15. Quality Standards

### 8.1 Code Quality
- Follow single responsibility principle
- Avoid premature abstractions
- DRY (Don't Repeat Yourself)
- Clear, readable code with comments where intent isn't obvious
- Consistent naming and formatting

### 8.2 Error Handling
- Graceful handling of invalid inputs
- Clear error messages
- Logging for debugging

### 8.3 State Management
- Correct state reset implementation (critical for L=1)
- Proper handling of hidden states in training loop

## 16. Success Criteria

1. Dataset generation produces correct shapes and values
2. LSTM model processes inputs and produces valid outputs
3. Training loop decreases loss over epochs
4. MSE_train and MSE_test are calculated correctly
5. Model generalizes well (MSE_test ≈ MSE_train)
6. Visualization graphs are generated correctly
7. All tests pass with documented expected results
8. Complete documentation following ex1 structure

## 17. Key Technical Points

1. **Sequence Length L=1:** Each sample is processed independently, but state is passed from one sample to the next
2. **State Management:** Critical for this exercise - do NOT reset `h_t` and `c_t` between consecutive samples; pass state from previous sample to current sample
3. **Conditional Input:** One-hot vector tells LSTM which frequency to extract
4. **Data Generation:** Two separate datasets with different seeds for train/test generalization check
5. **Noise Variation:** Amplitude and phase noise must vary at every sample `t`

## 18. Notes

- **State Management:** The correct implementation of state reset is critical for the exercise
- **Generalization:** Success depends on the model learning consistent frequency structure while ignoring random noise
- **Documentation:** Professional documentation is as important as working code
- **Modularity:** Code should be organized in clear modules for maintainability

