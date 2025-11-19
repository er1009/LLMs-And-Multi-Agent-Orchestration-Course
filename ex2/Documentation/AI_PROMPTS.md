# AI Prompts Documentation

This document tracks all prompts used with AI assistants during the development of the LSTM Signal Extraction project.

## Initial Project Setup

### Prompt 1: Project Structure Creation

```
Build ex2 directory according to these specs, you can also look at what ive done in ex1.
```

**Context:** User wanted to build ex2 following the same structure as ex1.

**Result:** Created complete directory structure with all necessary folders.

## Implementation Prompts

### Prompt 2: Complete Implementation Request

```
a) Complete implementation with dataset generation, LSTM training, and evaluation (full ML pipeline) write it in modules.
a) PyTorch (more manual control over LSTM state management)
a) Yes - same structure with PRD.md, README.md, Documentation folder, tests, src/ directory
a) Include training code that can be executed to train the model
```

**Context:** User specified requirements for the implementation.

**Result:** Created complete implementation with all modules.

## Key Implementation Details

### Dataset Generation

**Challenge:** Understanding the noise generation requirements.

**Prompt Used:**
- Analyzed homework PDF to understand noise generation requirements
- Implemented noisy signal generation with amplitude and phase noise at each sample

**Result:** Correct implementation of noisy signal generation.

### LSTM State Management

**Challenge:** Understanding the critical state management requirement for L=1.

**Prompt Used:**
- Analyzed homework requirements for state management
- Implemented explicit state management functionality (state NOT reset between consecutive samples)

**Result:** Correct implementation of state management for L=1 sequence length.

### Training Loop

**Challenge:** Ensuring state is managed correctly in training loop.

**Prompt Used:**
- Implemented training loop with state passed from one sample to the next (NOT reset between consecutive samples)
- Added proper MSE calculation

**Result:** Correct training loop implementation.

## Effective Prompts

### What Worked Well

1. **Clear Requirements:** Specifying exact requirements (PyTorch, modules, structure) helped create the right implementation.

2. **Reference to ex1:** Looking at ex1 structure helped maintain consistency.

3. **Modular Approach:** Requesting modular implementation helped organize the codebase.

### What Didn't Work

1. **Initial PDF Parsing:** Direct PDF parsing was challenging, but image descriptions helped.

2. **State Management Understanding:** Required careful analysis of homework requirements (state should NOT be reset between consecutive samples).

## Prompt Iterations

### Iteration 1: Initial Understanding

**Prompt:** "build ex2 dir according to these specs, you can also look at what ive done in ex1."

**Result:** Created directory structure, but needed clarification on implementation details.

### Iteration 2: Implementation Requirements

**Prompt:** User specified complete requirements (PyTorch, modules, full pipeline).

**Result:** Created complete implementation with all modules.

## Final Effective Prompts

### For Dataset Generation

```
Implement dataset generation with:
- Noisy signals with amplitude and phase noise at each sample
- Mixed signal S(t) = (1/4) * sum(Sinus_i^noisy)
- Pure targets Target_i(t) = sin(2π * f_i * t)
- Train/test sets with different seeds
```

### For LSTM Model

```
Implement LSTM model with:
- Input size 5 (1 signal + 4 one-hot selector)
- Output size 1 (predicted target)
- State management functionality for L=1 sequence length (state NOT reset between consecutive samples)
- Forward pass with optional hidden state
```

### For Training

```
Implement training loop with:
- MSE loss function
- Adam optimizer
- State passed from one sample to the next (NOT reset between consecutive samples, critical for L=1)
- MSE_train calculation
```

### For Evaluation

```
Implement evaluation with:
- MSE_test calculation
- Generalization checking (MSE_test ≈ MSE_train)
- Prediction generation for all frequencies
```

## Lessons Learned

1. **Clear Requirements:** Specifying exact requirements upfront helps create the right implementation.

2. **Modular Design:** Requesting modular implementation helps organize code.

3. **Reference Examples:** Looking at similar projects (ex1) helps maintain consistency.

4. **Iterative Refinement:** Iterating on prompts helps refine the implementation.

## Best Practices

1. **Be Specific:** Specify exact requirements (framework, structure, functionality).

2. **Provide Context:** Reference similar projects or examples.

3. **Request Modularity:** Ask for modular implementation for maintainability.

4. **Iterate:** Refine prompts based on results.

