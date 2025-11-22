"""
Graph Generator

Creates visualizations for analysis results, including:
- Scatter plots of error rate vs. semantic distance
- Trend lines and statistical overlays
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Optional


class GraphGenerator:
    """
    Generator for analysis graphs and visualizations.

    Creates publication-quality plots for analyzing the relationship
    between error rates and semantic drift.
    """

    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """
        Initialize the graph generator.

        Args:
            style: Matplotlib style to use for plots
        """
        try:
            plt.style.use(style)
        except:
            # Fallback to default if style not available
            plt.style.use("default")

    def generate_scatter_plot(
        self,
        error_rates: List[float],
        distances: List[float],
        output_path: str,
        title: str = "Semantic Drift vs. Error Rate",
        xlabel: str = "Spelling Error Rate",
        ylabel: str = "Cosine Distance",
        show_trend: bool = True,
        dpi: int = 300,
    ) -> None:
        """
        Generate a scatter plot of error rates vs. semantic distances.

        Args:
            error_rates: List of error rates (x-axis)
            distances: List of corresponding distances (y-axis)
            output_path: Path to save the plot (PNG)
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            show_trend: Whether to show trend line
            dpi: Resolution in dots per inch

        Raises:
            ValueError: If data lists have different lengths or are empty
        """
        if len(error_rates) != len(distances):
            raise ValueError(
                f"Error rates and distances must have same length, "
                f"got {len(error_rates)} and {len(distances)}"
            )

        if not error_rates:
            raise ValueError("Cannot create plot with empty data")

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create scatter plot
        ax.scatter(error_rates, distances, alpha=0.6, s=50, c="blue", label="Data points")

        # Add trend line if requested
        if show_trend and len(error_rates) > 1:
            z = np.polyfit(error_rates, distances, 1)
            p = np.poly1d(z)
            x_trend = np.linspace(min(error_rates), max(error_rates), 100)
            ax.plot(
                x_trend,
                p(x_trend),
                "r--",
                alpha=0.8,
                linewidth=2,
                label=f"Trend: y={z[0]:.4f}x+{z[1]:.4f}",
            )

        # Styling
        ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
        ax.legend(loc="best", framealpha=0.9)
        ax.grid(True, alpha=0.3)

        # Format axes
        ax.set_xlim(-0.02, max(error_rates) + 0.02)
        ax.set_ylim(min(0, min(distances) - 0.02), max(distances) + 0.02)

        # Tight layout
        plt.tight_layout()

        # Save figure
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
        plt.close()

    def generate_multi_metric_plot(
        self,
        error_rates: List[float],
        cosine_distances: List[float],
        euclidean_distances: List[float],
        output_path: str,
        title: str = "Semantic Drift Analysis (Multiple Metrics)",
        dpi: int = 300,
    ) -> None:
        """
        Generate a plot comparing multiple distance metrics.

        Args:
            error_rates: List of error rates (x-axis)
            cosine_distances: List of cosine distances
            euclidean_distances: List of Euclidean distances
            output_path: Path to save the plot (PNG)
            title: Plot title
            dpi: Resolution in dots per inch

        Raises:
            ValueError: If data lists have different lengths or are empty
        """
        if not (
            len(error_rates) == len(cosine_distances) == len(euclidean_distances)
        ):
            raise ValueError("All data lists must have the same length")

        if not error_rates:
            raise ValueError("Cannot create plot with empty data")

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Cosine distance plot
        ax1.scatter(error_rates, cosine_distances, alpha=0.6, s=50, c="blue")
        if len(error_rates) > 1:
            z1 = np.polyfit(error_rates, cosine_distances, 1)
            p1 = np.poly1d(z1)
            x_trend = np.linspace(min(error_rates), max(error_rates), 100)
            ax1.plot(x_trend, p1(x_trend), "r--", alpha=0.8, linewidth=2)
        ax1.set_xlabel("Spelling Error Rate", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Cosine Distance", fontsize=12, fontweight="bold")
        ax1.set_title("Cosine Distance", fontsize=13, fontweight="bold")
        ax1.grid(True, alpha=0.3)

        # Euclidean distance plot
        ax2.scatter(error_rates, euclidean_distances, alpha=0.6, s=50, c="green")
        if len(error_rates) > 1:
            z2 = np.polyfit(error_rates, euclidean_distances, 1)
            p2 = np.poly1d(z2)
            x_trend = np.linspace(min(error_rates), max(error_rates), 100)
            ax2.plot(x_trend, p2(x_trend), "r--", alpha=0.8, linewidth=2)
        ax2.set_xlabel("Spelling Error Rate", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Euclidean Distance", fontsize=12, fontweight="bold")
        ax2.set_title("Euclidean Distance", fontsize=13, fontweight="bold")
        ax2.grid(True, alpha=0.3)

        # Overall title
        fig.suptitle(title, fontsize=14, fontweight="bold", y=1.02)

        # Tight layout
        plt.tight_layout()

        # Save figure
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
        plt.close()

    def generate_histogram(
        self,
        distances: List[float],
        output_path: str,
        title: str = "Distribution of Semantic Distances",
        xlabel: str = "Cosine Distance",
        bins: int = 20,
        dpi: int = 300,
    ) -> None:
        """
        Generate a histogram of semantic distances.

        Args:
            distances: List of distances
            output_path: Path to save the plot (PNG)
            title: Plot title
            xlabel: X-axis label
            bins: Number of histogram bins
            dpi: Resolution in dots per inch

        Raises:
            ValueError: If distances list is empty
        """
        if not distances:
            raise ValueError("Cannot create histogram with empty data")

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create histogram
        n, bins, patches = ax.hist(
            distances, bins=bins, alpha=0.7, color="blue", edgecolor="black"
        )

        # Add mean line
        mean_dist = np.mean(distances)
        ax.axvline(
            mean_dist,
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Mean: {mean_dist:.4f}",
        )

        # Styling
        ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
        ax.set_ylabel("Frequency", fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
        ax.legend(loc="best", framealpha=0.9)
        ax.grid(True, alpha=0.3, axis="y")

        # Tight layout
        plt.tight_layout()

        # Save figure
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
        plt.close()
