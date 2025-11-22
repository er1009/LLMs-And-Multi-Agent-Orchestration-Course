#!/usr/bin/env python3
"""
Demo script showing all working components
(without Claude CLI dependency)
"""

import sys
sys.path.insert(0, 'src')

from translation import ErrorInjector
from evaluation import HuggingFaceEmbedding, EvaluationEngine
from analysis import GraphGenerator, StatisticsCalculator, ResultExporter

print("=" * 70)
print("DEMO: Multi-Agent Translation System Components")
print("=" * 70)
print()

# 1. Error Injection
print("1️⃣  Error Injection Demo")
print("-" * 70)

injector = ErrorInjector(seed=42)
original = "The quick brown fox jumps over the lazy dog and rests peacefully under a tree"

print(f"Original ({len(original.split())} words):")
print(f"  {original}")
print()

corrupted_low = injector.inject_errors(original, error_rate=0.15)
print("Corrupted (15% error rate):")
print(f"  {corrupted_low}")
print()

# 2. Embeddings & Evaluation
print("2️⃣  Semantic Similarity Evaluation")
print("-" * 70)

print("Initializing HuggingFace embeddings (local, no API)...")
embedder = HuggingFaceEmbedding(model_name='all-MiniLM-L6-v2')
engine = EvaluationEngine(embedder)

# Simulate translations with different quality
simulated_translations = [
    ("No errors (baseline)", original, 0.0),
    ("Minor changes", "The fast brown fox leaps over the sleepy dog and rests quietly under a tree", 0.1),
    ("Moderate changes", "A quick brown fox jumps across the lazy dog resting peacefully beneath the tree", 0.2),
    ("Significant changes", "The swift fox jumped over a dog and slept under the big tree", 0.3),
]

results = []
for label, translation, error_rate in simulated_translations:
    result = engine.evaluate(original, translation, error_rate=error_rate)
    results.append({
        'label': label,
        'error_rate': error_rate,
        'cosine_distance': result.cosine_distance,
        'euclidean_distance': result.euclidean_distance,
        'translation': translation
    })

    print(f"\n{label}:")
    print(f"  Translation: {translation}")
    print(f"  Cosine distance: {result.cosine_distance:.4f}")
    print(f"  Euclidean distance: {result.euclidean_distance:.4f}")

print()

# 3. Statistical Analysis
print("3️⃣  Statistical Analysis")
print("-" * 70)

error_rates = [r['error_rate'] for r in results]
distances = [r['cosine_distance'] for r in results]

calc = StatisticsCalculator()
trend = calc.calculate_trend(error_rates, distances)

print(f"Correlation coefficient: {trend.correlation:.4f}")
print(f"R² score: {trend.r_squared:.4f}")
print(f"Trend line: y = {trend.slope:.4f}x + {trend.intercept:.4f}")
print()

# 4. Graph Generation
print("4️⃣  Visualization")
print("-" * 70)

gen = GraphGenerator()
gen.generate_scatter_plot(
    error_rates=error_rates,
    distances=distances,
    output_path='results/graphs/demo_analysis.png',
    title='Demo: Simulated Semantic Drift Analysis',
    xlabel='Error Rate',
    ylabel='Cosine Distance',
    show_trend=True,
    dpi=200
)

print("✅ Graph generated: results/graphs/demo_analysis.png")
print()

# 5. Export Results
print("5️⃣  Data Export")
print("-" * 70)

# Export to JSON
exporter = ResultExporter()
export_data = [
    {
        'label': r['label'],
        'error_rate': r['error_rate'],
        'original': original,
        'translation': r['translation'],
        'cosine_distance': r['cosine_distance'],
        'euclidean_distance': r['euclidean_distance']
    }
    for r in results
]

exporter.export_json(export_data, 'results/demo_results.json')
print("✅ Results exported: results/demo_results.json")

exporter.export_csv(export_data, 'results/demo_results.csv')
print("✅ Results exported: results/demo_results.csv")
print()

# Summary
print("=" * 70)
print("✅ DEMO COMPLETE - All Components Working!")
print("=" * 70)
print()
print("Components Tested:")
print("  ✅ Error Injection (deterministic, reproducible)")
print("  ✅ HuggingFace Embeddings (local, no API key)")
print("  ✅ Semantic Distance Calculation (cosine, Euclidean)")
print("  ✅ Statistical Analysis (correlation, R²)")
print("  ✅ Graph Generation (matplotlib)")
print("  ✅ Data Export (JSON, CSV)")
print()
print("Next Step:")
print("  Install Claude CLI to enable full translation pipeline")
print("  Run: ./run.sh turing-machine --config machines/unary_increment.json --tape '111'")
print()
