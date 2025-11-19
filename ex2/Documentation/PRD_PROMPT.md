# PRD Prompt

This document contains the initial prompt used to create the Product Requirements Document (PRD) for the LSTM Signal Extraction project.

## Initial Prompt

The following prompt was used to generate the PRD:

```
Build a PyTorch-based LSTM system that performs conditional regression to extract 
individual frequency components from mixed noisy signals. The system should:

1. Generate noisy mixed signals from 4 different sine wave frequencies (1Hz, 3Hz, 5Hz, 7Hz)
2. Use a one-hot encoded frequency selector to tell the LSTM which frequency to extract
3. Train an LSTM to extract pure frequency components from the mixed signal
4. Evaluate generalization using train/test sets with different noise realizations
5. Generate visualizations comparing predictions vs targets

Key requirements:
- Sequence length L=1 with state reset between samples
- Two separate datasets (train/test) with different random seeds
- MSE calculation for both training and test sets
- Visualization of extracted frequencies
- Complete documentation following ex1 structure
```

## Context

This PRD was created based on the homework assignment specifications for Exercise 2, which involves:
- Signal processing with LSTM networks
- Conditional regression for frequency extraction
- State management in LSTM (L=1 sequence length)
- Dataset generation with noisy signals
- Model evaluation and generalization checking

## Notes

The PRD was structured to follow the same professional format as ex1, ensuring consistency across exercises while addressing the specific requirements of the LSTM signal extraction task.

