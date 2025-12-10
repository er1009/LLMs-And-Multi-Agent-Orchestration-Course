"""Visualization utilities for experiment results.

This module provides publication-quality visualizations for all experiments.
All graphs are generated at 300 DPI with proper labels, legends, and error bars.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd

from src.config.settings import config

logger = logging.getLogger(__name__)

# Set publication-quality defaults
matplotlib.rcParams['figure.dpi'] = 100  # Display DPI
matplotlib.rcParams['savefig.dpi'] = config.graph_dpi  # Save DPI
matplotlib.rcParams['font.size'] = 11
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['axes.labelsize'] = 12
matplotlib.rcParams['axes.titlesize'] = 14
matplotlib.rcParams['xtick.labelsize'] = 10
matplotlib.rcParams['ytick.labelsize'] = 10
matplotlib.rcParams['legend.fontsize'] = 10


def plot_lost_in_middle(
    results: Dict[str, List[float]],
    output_path: Optional[str] = None,
    show: bool = False
) -> None:
    """Create bar graph for Experiment 1: Lost in the Middle.

    Args:
        results: Dictionary with keys "start", "middle", "end"
                 and values as lists of accuracy scores
        output_path: Path to save graph (PNG)
        show: Whether to display graph interactively

    Example:
        >>> results = {
        ...     "start": [0.9, 0.95, 0.92],
        ...     "middle": [0.6, 0.55, 0.58],
        ...     "end": [0.88, 0.91, 0.90]
        ... }
        >>> plot_lost_in_middle(results, "exp1.png")
    """
    positions = ['Start', 'Middle', 'End']
    accuracies = [
        np.mean(results['start']) * 100,
        np.mean(results['middle']) * 100,
        np.mean(results['end']) * 100
    ]
    std_devs = [
        np.std(results['start']) * 100,
        np.std(results['middle']) * 100,
        np.std(results['end']) * 100
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create bars with distinct colors
    colors = ['#2ecc71', '#e74c3c', '#3498db']  # Green, Red, Blue
    bars = ax.bar(
        positions,
        accuracies,
        yerr=std_devs,
        capsize=10,
        color=colors,
        alpha=0.8,
        edgecolor='black',
        linewidth=1.5
    )

    # Labels and title
    ax.set_ylabel('Accuracy (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Fact Position in Document', fontsize=14, fontweight='bold')
    ax.set_title(
        'Lost in the Middle: Accuracy by Position',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.,
            height + 5,
            f'{acc:.1f}%',
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=12
        )

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=config.graph_dpi, bbox_inches='tight')
        logger.info(f"Saved graph to {output_path}")

    if show:
        plt.show()

    plt.close()


def plot_context_size_impact(
    results: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    show: bool = False
) -> None:
    """Create dual-axis graph for Experiment 2: Context Size Impact.

    Args:
        results: List of result dictionaries with keys:
                 "num_docs", "accuracy", "latency"
        output_path: Path to save graph (PNG)
        show: Whether to display graph interactively

    Example:
        >>> results = [
        ...     {"num_docs": 2, "accuracy": 0.95, "latency": 800},
        ...     {"num_docs": 5, "accuracy": 0.85, "latency": 1500},
        ...     {"num_docs": 10, "accuracy": 0.70, "latency": 2500}
        ... ]
        >>> plot_context_size_impact(results, "exp2.png")
    """
    doc_counts = [r['num_docs'] for r in results]
    accuracies = [r['accuracy'] * 100 for r in results]
    latencies = [r['latency'] for r in results]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Accuracy line (left y-axis)
    color1 = '#2ecc71'
    ax1.set_xlabel('Number of Documents', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', color=color1, fontsize=14, fontweight='bold')
    line1 = ax1.plot(
        doc_counts,
        accuracies,
        color=color1,
        marker='o',
        linewidth=3,
        markersize=8,
        label='Accuracy'
    )
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, 100)
    ax1.grid(alpha=0.3, linestyle='--')

    # Latency line (right y-axis)
    ax2 = ax1.twinx()
    color2 = '#e74c3c'
    ax2.set_ylabel('Latency (ms)', color=color2, fontsize=14, fontweight='bold')
    line2 = ax2.plot(
        doc_counts,
        latencies,
        color=color2,
        marker='s',
        linewidth=3,
        markersize=8,
        label='Latency'
    )
    ax2.tick_params(axis='y', labelcolor=color2)

    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=12, framealpha=0.9)

    plt.title(
        'Context Window Size Impact on Performance',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=config.graph_dpi, bbox_inches='tight')
        logger.info(f"Saved graph to {output_path}")

    if show:
        plt.show()

    plt.close()


def plot_rag_comparison(
    rag_results: Dict[str, float],
    full_results: Dict[str, float],
    output_path: Optional[str] = None,
    show: bool = False
) -> None:
    """Create comparison graph for Experiment 3: RAG vs Full Context.

    Args:
        rag_results: Dictionary with "accuracy", "latency", "tokens"
        full_results: Dictionary with "accuracy", "latency", "tokens"
        output_path: Path to save graph (PNG)
        show: Whether to display graph interactively

    Example:
        >>> rag_results = {"accuracy": 0.92, "latency": 1200, "tokens": 800}
        >>> full_results = {"accuracy": 0.65, "latency": 4300, "tokens": 4500}
        >>> plot_rag_comparison(rag_results, full_results, "exp3.png")
    """
    metrics = ['Accuracy (%)', 'Latency (ms)', 'Tokens Used']
    rag_values = [
        rag_results['accuracy'] * 100,
        rag_results['latency'],
        rag_results['tokens']
    ]
    full_values = [
        full_results['accuracy'] * 100,
        full_results['latency'],
        full_results['tokens']
    ]

    # Normalize values for better visualization
    # We'll create 3 subplots for each metric
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    approaches = ['RAG', 'Full Context']
    colors = ['#3498db', '#95a5a6']

    for idx, (ax, metric) in enumerate(zip(axes, metrics)):
        values = [rag_values[idx], full_values[idx]]

        bars = ax.bar(approaches, values, color=colors, alpha=0.8, edgecolor='black')

        ax.set_ylabel(metric, fontsize=12, fontweight='bold')
        ax.set_title(metric, fontsize=13, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{val:.0f}' if metric != 'Accuracy (%)' else f'{val:.1f}%',
                ha='center',
                va='bottom',
                fontweight='bold',
                fontsize=11
            )

        # Calculate improvement
        if metric == 'Accuracy (%)':
            improvement = ((rag_values[idx] - full_values[idx]) / full_values[idx]) * 100
            ax.text(
                0.5, 0.95,
                f'RAG: +{improvement:.1f}% better',
                transform=ax.transAxes,
                ha='center',
                va='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5),
                fontsize=9
            )
        else:
            improvement = ((full_values[idx] - rag_values[idx]) / full_values[idx]) * 100
            ax.text(
                0.5, 0.95,
                f'RAG: {improvement:.1f}% less',
                transform=ax.transAxes,
                ha='center',
                va='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5),
                fontsize=9
            )

    plt.suptitle(
        'RAG vs Full Context Comparison',
        fontsize=16,
        fontweight='bold',
        y=1.02
    )
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=config.graph_dpi, bbox_inches='tight')
        logger.info(f"Saved graph to {output_path}")

    if show:
        plt.show()

    plt.close()


def create_strategy_comparison_table(
    results: List[Dict[str, Any]],
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """Create comparison table for Experiment 4: Context Strategies.

    Args:
        results: List of result dictionaries with keys:
                 "action", "strategy", "context_tokens", "latency", "accuracy"
        output_path: Path to save table (CSV or MD)

    Returns:
        DataFrame with aggregated statistics

    Example:
        >>> results = [
        ...     {"strategy": "select", "context_tokens": 500, "latency": 800, "accuracy": 0.9},
        ...     {"strategy": "select", "context_tokens": 600, "latency": 850, "accuracy": 0.92},
        ...     {"strategy": "compress", "context_tokens": 800, "latency": 1200, "accuracy": 0.85}
        ... ]
        >>> df = create_strategy_comparison_table(results, "exp4.csv")
    """
    df = pd.DataFrame(results)

    # Calculate averages per strategy
    summary = df.groupby('strategy').agg({
        'context_tokens': ['mean', 'std'],
        'latency': ['mean', 'std'],
        'accuracy': ['mean', 'std']
    }).round(2)

    # Flatten column names
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()

    # Rename for clarity
    summary.columns = [
        'Strategy',
        'Avg Tokens', 'Std Tokens',
        'Avg Latency (ms)', 'Std Latency',
        'Avg Accuracy', 'Std Accuracy'
    ]

    if output_path:
        ext = Path(output_path).suffix

        if ext == '.csv':
            summary.to_csv(output_path, index=False)
            logger.info(f"Saved table to {output_path}")

        elif ext == '.md':
            md_table = summary.to_markdown(index=False)
            with open(output_path, 'w') as f:
                f.write("# Strategy Comparison Results\n\n")
                f.write(md_table)
            logger.info(f"Saved markdown table to {output_path}")

    return summary


def plot_strategy_trends(
    results: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    show: bool = False
) -> None:
    """Create trend graph for Experiment 4: Context Strategies over time.

    Args:
        results: List of result dictionaries
        output_path: Path to save graph (PNG)
        show: Whether to display graph interactively
    """
    df = pd.DataFrame(results)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    strategies = df['strategy'].unique()
    colors = {'select': '#3498db', 'compress': '#e74c3c', 'write': '#2ecc71'}

    # Plot 1: Context Tokens over Actions
    ax = axes[0]
    for strategy in strategies:
        strategy_df = df[df['strategy'] == strategy]
        ax.plot(
            strategy_df['action'],
            strategy_df['context_tokens'],
            marker='o',
            label=strategy.upper(),
            color=colors.get(strategy, '#95a5a6'),
            linewidth=2
        )
    ax.set_xlabel('Action Number', fontweight='bold')
    ax.set_ylabel('Context Tokens', fontweight='bold')
    ax.set_title('Context Growth Over Time', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Plot 2: Latency over Actions
    ax = axes[1]
    for strategy in strategies:
        strategy_df = df[df['strategy'] == strategy]
        ax.plot(
            strategy_df['action'],
            strategy_df['latency'],
            marker='s',
            label=strategy.upper(),
            color=colors.get(strategy, '#95a5a6'),
            linewidth=2
        )
    ax.set_xlabel('Action Number', fontweight='bold')
    ax.set_ylabel('Latency (ms)', fontweight='bold')
    ax.set_title('Latency Over Time', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Plot 3: Accuracy over Actions
    ax = axes[2]
    for strategy in strategies:
        strategy_df = df[df['strategy'] == strategy]
        ax.plot(
            strategy_df['action'],
            strategy_df['accuracy'] * 100,
            marker='^',
            label=strategy.upper(),
            color=colors.get(strategy, '#95a5a6'),
            linewidth=2
        )
    ax.set_xlabel('Action Number', fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_title('Accuracy Over Time', fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(alpha=0.3)

    plt.suptitle(
        'Context Engineering Strategies Comparison',
        fontsize=16,
        fontweight='bold',
        y=1.02
    )
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=config.graph_dpi, bbox_inches='tight')
        logger.info(f"Saved graph to {output_path}")

    if show:
        plt.show()

    plt.close()
