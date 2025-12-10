"""Base experiment class for all experiments.

This module defines the abstract base class that all experiments must inherit from,
ensuring a consistent interface and implementation pattern.
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseExperiment(ABC):
    """Abstract base class for all context window experiments.

    Provides common functionality for:
    - Running experiments with multiple trials
    - Saving results to disk
    - Generating visualizations
    - Statistical analysis

    Subclasses must implement:
    - run_single_trial()
    - run_full_experiment()
    - visualize_results()
    """

    def __init__(
        self,
        experiment_name: str,
        model: str = "llama2",
        random_seed: Optional[int] = None
    ):
        """Initialize base experiment.

        Args:
            experiment_name: Human-readable experiment name
            model: LLM model to use
            random_seed: Random seed for reproducibility
        """
        self.experiment_name = experiment_name
        self.model = model
        self.random_seed = random_seed

        logger.info(
            f"Initialized {experiment_name} with model={model}, seed={random_seed}"
        )

    @abstractmethod
    def run_single_trial(self, *args, **kwargs) -> Dict[str, Any]:
        """Run a single trial of the experiment.

        Returns:
            Dictionary with trial results
        """
        pass

    @abstractmethod
    def run_full_experiment(
        self,
        num_runs: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Run complete experiment with multiple trials.

        Args:
            num_runs: Number of trials for statistical validity
            **kwargs: Experiment-specific parameters

        Returns:
            Dictionary with complete results, statistics, and metadata
        """
        pass

    @abstractmethod
    def visualize_results(
        self,
        results: Dict[str, Any],
        output_dir: str
    ) -> None:
        """Generate and save visualizations.

        Args:
            results: Results dictionary from run_full_experiment()
            output_dir: Directory to save visualizations
        """
        pass

    def save_results(
        self,
        results: Dict[str, Any],
        output_dir: str,
        save_raw: bool = True
    ) -> None:
        """Save experiment results to disk.

        Args:
            results: Results dictionary
            output_dir: Output directory
            save_raw: Whether to save raw JSON results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if save_raw:
            # Save complete results as JSON
            json_path = output_path / "raw_results.json"
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Saved raw results to {json_path}")

        # Save statistics as CSV if available
        if "statistics" in results:
            import pandas as pd

            stats_df = pd.DataFrame([results["statistics"]])
            csv_path = output_path / "aggregated_stats.csv"
            stats_df.to_csv(csv_path, index=False)
            logger.info(f"Saved statistics to {csv_path}")

    def create_result_structure(
        self,
        trials: list,
        config: Dict[str, Any],
        total_runtime: float
    ) -> Dict[str, Any]:
        """Create standardized result structure.

        Args:
            trials: List of trial result dictionaries
            config: Experiment configuration
            total_runtime: Total execution time in seconds

        Returns:
            Standardized result dictionary
        """
        import numpy as np

        # Calculate statistics from trials
        accuracies = [t.get('accuracy', 0.0) for t in trials]
        latencies = [t.get('latency_ms', 0.0) for t in trials]

        success_count = sum(1 for t in trials if not t.get('error'))

        # Calculate confidence interval (95%)
        if len(accuracies) > 1:
            std_error = np.std(accuracies) / np.sqrt(len(accuracies))
            confidence_margin = 1.96 * std_error  # 95% CI
            ci_lower = max(0, np.mean(accuracies) - confidence_margin)
            ci_upper = min(1, np.mean(accuracies) + confidence_margin)
        else:
            ci_lower = ci_upper = np.mean(accuracies) if accuracies else 0

        return {
            "experiment_id": self.experiment_name.lower().replace(" ", "_"),
            "timestamp": datetime.now().isoformat(),
            "config": config,
            "trials": trials,
            "statistics": {
                "mean_accuracy": float(np.mean(accuracies)) if accuracies else 0.0,
                "std_accuracy": float(np.std(accuracies)) if accuracies else 0.0,
                "min_accuracy": float(np.min(accuracies)) if accuracies else 0.0,
                "max_accuracy": float(np.max(accuracies)) if accuracies else 0.0,
                "mean_latency": float(np.mean(latencies)) if latencies else 0.0,
                "std_latency": float(np.std(latencies)) if latencies else 0.0,
                "confidence_interval_95": [float(ci_lower), float(ci_upper)],
            },
            "metadata": {
                "total_runtime_seconds": total_runtime,
                "success_rate": success_count / len(trials) if trials else 0.0,
                "num_trials": len(trials),
                "failed_trials": len(trials) - success_count,
            }
        }
