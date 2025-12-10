# Analysis Notebooks

This directory contains Jupyter notebooks for analyzing experiment results.

## Notebooks

1. **01_experiment1_analysis.ipynb** - Analysis of Needle in Haystack results
   - Statistical significance testing
   - Position-based accuracy comparison
   - Visualization of lost-in-the-middle effect

2. **02_experiment2_analysis.ipynb** - Analysis of Context Size Impact
   - Accuracy degradation trends
   - Latency analysis
   - Token usage patterns

3. **03_experiment3_analysis.ipynb** - Analysis of RAG vs Full Context
   - Performance comparison
   - Cost-benefit analysis
   - Retrieval effectiveness

4. **04_experiment4_analysis.ipynb** - Analysis of Context Strategies
   - Strategy comparison
   - Context growth patterns
   - Accuracy-latency tradeoffs

5. **05_combined_analysis.ipynb** - Combined analysis of all experiments
   - Cross-experiment insights
   - Recommendations
   - Research findings

## Usage

```bash
# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

## Requirements

All notebooks require the experiment results to be generated first:

```bash
# Run all experiments
python main.py --all

# Or run individually
python main.py --experiment 1
python main.py --experiment 2
python main.py --experiment 3
python main.py --experiment 4
```

Results will be saved to `../results/experimentN/` directories.

## Analysis Features

Each notebook includes:
- Data loading and preprocessing
- Summary statistics
- Statistical significance testing
- Publication-quality visualizations
- Error analysis
- Conclusions and insights

## Customization

You can customize the analysis by:
1. Modifying visualization parameters
2. Adding custom statistical tests
3. Comparing multiple experiment runs
4. Exporting results in different formats
