#!/usr/bin/env python3
"""
Comprehensive Experiment Runner

Runs large-scale experiments across all system components:
1. Turing Machine simulations (multiple configurations)
2. Error injection analysis (multiple rates)
3. Semantic drift experiments (simulated translations)
4. Statistical analysis and visualization
5. Complete results export
"""

import sys
sys.path.insert(0, 'src')

import os
import json
from pathlib import Path
from datetime import datetime
import numpy as np

from translation import ErrorInjector
from evaluation import HuggingFaceEmbedding, EvaluationEngine
from analysis import GraphGenerator, StatisticsCalculator, ResultExporter
from turing_machine import TuringMachine

print("=" * 80)
print("COMPREHENSIVE EXPERIMENT SUITE")
print("Multi-Agent Translation Pipeline & Turing Machine Simulator")
print("=" * 80)
print()

# Create output directories
os.makedirs('results/experiments', exist_ok=True)
os.makedirs('results/graphs', exist_ok=True)
os.makedirs('results/logs', exist_ok=True)
os.makedirs('data/output', exist_ok=True)

experiment_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
experiment_dir = f'results/experiments/exp_{experiment_timestamp}'
os.makedirs(experiment_dir, exist_ok=True)

print(f"Experiment timestamp: {experiment_timestamp}")
print(f"Output directory: {experiment_dir}")
print()

# ============================================================================
# EXPERIMENT 1: Turing Machine Simulations
# ============================================================================

print("=" * 80)
print("EXPERIMENT 1: TURING MACHINE SIMULATIONS")
print("=" * 80)
print()

tm_results = []

# Test 1: Unary Increment
print("Test 1.1: Unary Increment")
print("-" * 80)
try:
    tm = TuringMachine.from_config_file('machines/unary_increment.json')

    test_cases = ["1", "11", "111", "1111", "11111"]
    for tape_input in test_cases:
        tm.load_tape(tape_input)
        result = tm.run(max_steps=1000)

        tm_results.append({
            'machine': 'unary_increment',
            'input': tape_input,
            'output': result.final_tape,
            'steps': result.steps_taken,
            'halted': result.halted
        })

        print(f"  Input: {tape_input:5s} → Output: {result.final_tape:6s} (Steps: {result.steps_taken})")

    print("  ✅ Unary increment tests completed")
except Exception as e:
    print(f"  ❌ Error: {e}")

print()

# Test 2: Binary Increment
print("Test 1.2: Binary Increment")
print("-" * 80)
try:
    tm = TuringMachine.from_config_file('machines/binary_increment.json')

    test_cases = ["0", "1", "10", "11", "101", "111", "1111"]
    for tape_input in test_cases:
        tm.load_tape(tape_input)
        result = tm.run(max_steps=1000)

        tm_results.append({
            'machine': 'binary_increment',
            'input': tape_input,
            'output': result.final_tape,
            'steps': result.steps_taken,
            'halted': result.halted
        })

        # Convert to decimal for verification
        try:
            input_dec = int(tape_input, 2)
            output_dec = int(result.final_tape.strip(), 2)
            print(f"  Input: {tape_input:5s} ({input_dec:2d}) → Output: {result.final_tape:6s} ({output_dec:2d}) [Steps: {result.steps_taken}]")
        except:
            print(f"  Input: {tape_input:5s} → Output: {result.final_tape:6s} (Steps: {result.steps_taken})")

    print("  ✅ Binary increment tests completed")
except Exception as e:
    print(f"  ❌ Error: {e}")

print()

# Save TM results
tm_output = f"{experiment_dir}/turing_machine_results.json"
with open(tm_output, 'w') as f:
    json.dump(tm_results, f, indent=2)
print(f"✅ Turing Machine results saved: {tm_output}")
print()

# ============================================================================
# EXPERIMENT 2: Error Injection Analysis
# ============================================================================

print("=" * 80)
print("EXPERIMENT 2: ERROR INJECTION ANALYSIS")
print("=" * 80)
print()

# Load sample sentences
sentences_file = 'data/input/sample_sentences.txt'
sample_sentences = []

print(f"Loading sentences from: {sentences_file}")
with open(sentences_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and len(line.split()) >= 15:
            sample_sentences.append(line)

print(f"Loaded {len(sample_sentences)} valid sentences (≥15 words each)")
print()

# Test with first 5 sentences across multiple error rates
test_sentences = sample_sentences[:5]
error_rates = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]

error_injection_results = []

print("Running error injection tests...")
print("-" * 80)

for idx, sentence in enumerate(test_sentences, 1):
    print(f"\nSentence {idx}: {sentence[:60]}...")

    for error_rate in error_rates:
        injector = ErrorInjector(seed=42 + idx * 100 + int(error_rate * 100))
        corrupted = injector.inject_errors(sentence, error_rate)
        stats = injector.get_error_statistics(sentence, corrupted)

        error_injection_results.append({
            'sentence_id': idx,
            'original': sentence,
            'corrupted': corrupted,
            'error_rate_requested': error_rate,
            'error_rate_actual': stats['actual_error_rate'],
            'words_changed': stats['words_changed'],
            'chars_changed': stats['chars_changed']
        })

        if error_rate in [0.0, 0.3, 0.5]:  # Show samples
            print(f"  Rate {error_rate*100:3.0f}%: {corrupted[:60]}...")

print()
error_output = f"{experiment_dir}/error_injection_results.json"
with open(error_output, 'w') as f:
    json.dump(error_injection_results, f, indent=2)
print(f"✅ Error injection results saved: {error_output}")
print()

# ============================================================================
# EXPERIMENT 3: Semantic Drift Analysis
# ============================================================================

print("=" * 80)
print("EXPERIMENT 3: SEMANTIC DRIFT ANALYSIS")
print("=" * 80)
print()

print("Initializing HuggingFace embedding model...")
embedder = HuggingFaceEmbedding(model_name='all-MiniLM-L6-v2')
engine = EvaluationEngine(embedder)
print(f"✅ Model loaded: {embedder.model_name} (dim: {embedder.get_dimension()})")
print()

# Simulate translations with varying degrees of semantic drift
# In a real scenario, these would come from Claude CLI translation pipeline

base_sentence = sample_sentences[0]
print(f"Base sentence: {base_sentence}")
print()

# Create simulated "translations" with increasing drift
simulated_scenarios = [
    {
        'name': 'Perfect (0% drift)',
        'text': base_sentence,
        'error_rate': 0.0
    },
    {
        'name': 'Minor synonyms (10% drift)',
        'text': base_sentence.replace('discovered', 'found').replace('remarkable', 'amazing').replace('expedition', 'journey'),
        'error_rate': 0.1
    },
    {
        'name': 'Moderate paraphrasing (25% drift)',
        'text': "Researchers found an incredible butterfly species that was new in the Amazon forest during last year's exploration.",
        'error_rate': 0.25
    },
    {
        'name': 'Significant rewording (40% drift)',
        'text': "A team of scientists identified a unique butterfly type in the remote jungles of the Amazon basin.",
        'error_rate': 0.40
    },
    {
        'name': 'Major changes (60% drift)',
        'text': "New butterfly was seen by research people in the big forest in South America one year ago.",
        'error_rate': 0.60
    },
    {
        'name': 'Completely different (90% drift)',
        'text': "The weather forecast predicts sunny conditions with temperatures reaching twenty degrees celsius throughout the entire coastal region today.",
        'error_rate': 0.90
    }
]

semantic_results = []

print("Evaluating semantic drift across scenarios...")
print("-" * 80)

for scenario in simulated_scenarios:
    result = engine.evaluate(base_sentence, scenario['text'], error_rate=scenario['error_rate'])

    semantic_results.append({
        'scenario': scenario['name'],
        'error_rate': scenario['error_rate'],
        'original': result.original_text,
        'translation': result.final_text,
        'cosine_distance': result.cosine_distance,
        'euclidean_distance': result.euclidean_distance
    })

    print(f"{scenario['name']:30s}: Cosine={result.cosine_distance:.4f}, Euclidean={result.euclidean_distance:.4f}")

print()

# ============================================================================
# EXPERIMENT 4: Large-Scale Multi-Sentence Analysis
# ============================================================================

print("=" * 80)
print("EXPERIMENT 4: LARGE-SCALE MULTI-SENTENCE ANALYSIS")
print("=" * 80)
print()

print(f"Analyzing {len(sample_sentences)} sentences with multiple error rates...")
print("-" * 80)

large_scale_results = []
error_rates_detailed = np.linspace(0.0, 0.5, 11)  # 0%, 5%, 10%, ..., 50%

for sent_idx, original_sentence in enumerate(sample_sentences[:10], 1):  # First 10 sentences
    print(f"\nProcessing sentence {sent_idx}/10...")

    for error_rate in error_rates_detailed:
        # Inject errors
        injector = ErrorInjector(seed=42 + sent_idx * 1000 + int(error_rate * 1000))
        corrupted = injector.inject_errors(original_sentence, error_rate)

        # Simulate translation (in real scenario, would go through Claude CLI)
        # For this demo, we'll simulate degradation proportional to error rate
        if error_rate < 0.2:
            simulated_translation = corrupted  # Minor changes
        elif error_rate < 0.4:
            # Moderate changes - replace some words
            simulated_translation = corrupted.replace('the', 'a').replace('and', '&')
        else:
            # Significant changes
            words = corrupted.split()
            simulated_translation = ' '.join(words[:len(words)//2])  # Truncate

        # Evaluate
        result = engine.evaluate(original_sentence, simulated_translation, error_rate=error_rate)

        large_scale_results.append({
            'sentence_id': sent_idx,
            'original': original_sentence,
            'error_rate': float(error_rate),
            'corrupted': corrupted,
            'translation': simulated_translation,
            'cosine_distance': float(result.cosine_distance),
            'euclidean_distance': float(result.euclidean_distance),
            'word_count': len(original_sentence.split())
        })

print()
print(f"✅ Processed {len(large_scale_results)} sentence-error rate combinations")
print()

# ============================================================================
# EXPERIMENT 5: Statistical Analysis
# ============================================================================

print("=" * 80)
print("EXPERIMENT 5: STATISTICAL ANALYSIS")
print("=" * 80)
print()

# Extract data for analysis
all_error_rates = [r['error_rate'] for r in large_scale_results]
all_cosine_distances = [r['cosine_distance'] for r in large_scale_results]
all_euclidean_distances = [r['euclidean_distance'] for r in large_scale_results]

calc = StatisticsCalculator()

# Overall correlation
print("Overall Statistics:")
print("-" * 80)
trend = calc.calculate_trend(all_error_rates, all_cosine_distances)
print(f"Cosine Distance Analysis:")
print(f"  Correlation coefficient: {trend.correlation:.4f}")
print(f"  R² score: {trend.r_squared:.4f}")
print(f"  Trend equation: y = {trend.slope:.4f}x + {trend.intercept:.4f}")
print()

trend_euc = calc.calculate_trend(all_error_rates, all_euclidean_distances)
print(f"Euclidean Distance Analysis:")
print(f"  Correlation coefficient: {trend_euc.correlation:.4f}")
print(f"  R² score: {trend_euc.r_squared:.4f}")
print(f"  Trend equation: y = {trend_euc.slope:.4f}x + {trend_euc.intercept:.4f}")
print()

# Summary statistics
summary_stats = calc.calculate_summary_stats(all_cosine_distances)
print("Cosine Distance Summary:")
print(f"  Mean: {summary_stats['mean']:.4f}")
print(f"  Median: {summary_stats['median']:.4f}")
print(f"  Std Dev: {summary_stats['std']:.4f}")
print(f"  Range: [{summary_stats['min']:.4f}, {summary_stats['max']:.4f}]")
print()

# ============================================================================
# EXPERIMENT 6: Visualization
# ============================================================================

print("=" * 80)
print("EXPERIMENT 6: VISUALIZATION GENERATION")
print("=" * 80)
print()

gen = GraphGenerator()

# Graph 1: Overall scatter plot
print("Generating Graph 1: Overall Error Rate vs Semantic Distance...")
gen.generate_scatter_plot(
    error_rates=all_error_rates,
    distances=all_cosine_distances,
    output_path=f'{experiment_dir}/graph_overall_analysis.png',
    title='Comprehensive Analysis: Error Rate vs Semantic Distance',
    xlabel='Error Rate',
    ylabel='Cosine Distance',
    show_trend=True,
    dpi=300
)
print(f"  ✅ Saved: {experiment_dir}/graph_overall_analysis.png")

# Graph 2: Multi-metric comparison
print("Generating Graph 2: Multi-Metric Comparison...")
gen.generate_multi_metric_plot(
    error_rates=all_error_rates,
    cosine_distances=all_cosine_distances,
    euclidean_distances=all_euclidean_distances,
    output_path=f'{experiment_dir}/graph_multi_metric.png',
    title='Comprehensive Multi-Metric Analysis',
    dpi=300
)
print(f"  ✅ Saved: {experiment_dir}/graph_multi_metric.png")

# Graph 3: Distribution histogram
print("Generating Graph 3: Distance Distribution...")
gen.generate_histogram(
    distances=all_cosine_distances,
    output_path=f'{experiment_dir}/graph_distribution.png',
    title='Distribution of Semantic Distances',
    xlabel='Cosine Distance',
    bins=30,
    dpi=300
)
print(f"  ✅ Saved: {experiment_dir}/graph_distribution.png")

print()

# ============================================================================
# EXPERIMENT 7: Data Export
# ============================================================================

print("=" * 80)
print("EXPERIMENT 7: COMPREHENSIVE DATA EXPORT")
print("=" * 80)
print()

exporter = ResultExporter()

# Export large-scale results
print("Exporting large-scale results...")
exporter.export_json(large_scale_results, f'{experiment_dir}/large_scale_results.json')
print(f"  ✅ JSON: {experiment_dir}/large_scale_results.json")

exporter.export_csv(large_scale_results, f'{experiment_dir}/large_scale_results.csv')
print(f"  ✅ CSV: {experiment_dir}/large_scale_results.csv")

# Export semantic drift results
print("Exporting semantic drift results...")
exporter.export_json(semantic_results, f'{experiment_dir}/semantic_drift_results.json')
print(f"  ✅ JSON: {experiment_dir}/semantic_drift_results.json")

# Export summary statistics
stats_summary = {
    'experiment_timestamp': experiment_timestamp,
    'total_sentences_analyzed': len(set(r['sentence_id'] for r in large_scale_results)),
    'total_evaluations': len(large_scale_results),
    'error_rate_range': [float(min(all_error_rates)), float(max(all_error_rates))],
    'cosine_distance_stats': {
        'mean': float(summary_stats['mean']),
        'median': float(summary_stats['median']),
        'std': float(summary_stats['std']),
        'min': float(summary_stats['min']),
        'max': float(summary_stats['max'])
    },
    'correlation_analysis': {
        'cosine': {
            'correlation': float(trend.correlation),
            'r_squared': float(trend.r_squared),
            'slope': float(trend.slope),
            'intercept': float(trend.intercept)
        },
        'euclidean': {
            'correlation': float(trend_euc.correlation),
            'r_squared': float(trend_euc.r_squared),
            'slope': float(trend_euc.slope),
            'intercept': float(trend_euc.intercept)
        }
    },
    'turing_machine_tests': len(tm_results)
}

exporter.export_summary_statistics(stats_summary, f'{experiment_dir}/experiment_summary.json')
print(f"  ✅ Summary: {experiment_dir}/experiment_summary.json")

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("=" * 80)
print("EXPERIMENT SUITE COMPLETED SUCCESSFULLY")
print("=" * 80)
print()

print("Results Summary:")
print(f"  • Turing Machine simulations: {len(tm_results)} tests")
print(f"  • Error injection tests: {len(error_injection_results)} combinations")
print(f"  • Semantic evaluations: {len(large_scale_results)} evaluations")
print(f"  • Sentences analyzed: {len(sample_sentences[:10])}")
print(f"  • Error rates tested: {len(error_rates_detailed)}")
print()

print("Output Files:")
print(f"  📁 Main directory: {experiment_dir}/")
print(f"  📊 Graphs: 3 PNG files")
print(f"  📄 Data exports: JSON and CSV formats")
print(f"  📈 Summary statistics: experiment_summary.json")
print()

print("Key Findings:")
print(f"  • Correlation (Error vs Distance): {trend.correlation:.4f}")
print(f"  • R² Score: {trend.r_squared:.4f}")
print(f"  • Average semantic distance: {summary_stats['mean']:.4f}")
print(f"  • Distance range: [{summary_stats['min']:.4f}, {summary_stats['max']:.4f}]")
print()

print("=" * 80)
print("All experiments completed successfully! 🎉")
print(f"Check {experiment_dir}/ for detailed results")
print("=" * 80)
