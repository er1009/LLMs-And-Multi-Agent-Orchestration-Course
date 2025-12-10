"""Experiment 1: Needle in Haystack (Lost in the Middle).

This experiment demonstrates that LLMs struggle to retrieve information
from the middle of long contexts.
"""

import logging
import time
from typing import Dict, Any, List
from pathlib import Path

from src.experiments.base import BaseExperiment
from src.utils.ollama_client import OllamaClient
from src.utils.document_generator import DocumentGenerator
from src.utils.evaluation import evaluate_response
from src.utils.tokenization import count_tokens
from src.utils.visualization import plot_lost_in_middle

logger = logging.getLogger(__name__)


class NeedleHaystackExperiment(BaseExperiment):
    """Experiment to test 'Lost in the Middle' phenomenon.

    Tests LLM's ability to retrieve facts from different positions
    in a long document (start, middle, end).

    Attributes:
        client: Ollama client for LLM queries
        doc_generator: Document generator for creating test documents
        haystack_words: Size of haystack document in words
    """

    def __init__(
        self,
        model: str = "llama2",
        random_seed: int = 42,
        haystack_words: int = 1000
    ):
        """Initialize Needle in Haystack experiment.

        Args:
            model: LLM model name
            random_seed: Random seed for reproducibility
            haystack_words: Number of words in haystack document
        """
        super().__init__(
            experiment_name="Needle in Haystack",
            model=model,
            random_seed=random_seed
        )

        self.haystack_words = haystack_words
        self.client = OllamaClient(model=model)
        self.doc_generator = DocumentGenerator(random_seed=random_seed)

        logger.info(f"Initialized with haystack_words={haystack_words}")

    def run_single_trial(
        self,
        position: str,
        needle: str,
        question: str
    ) -> Dict[str, Any]:
        """Run a single trial of the needle-in-haystack test.

        Args:
            position: Where to place needle ("start", "middle", "end")
            needle: The critical fact to embed
            question: Question to ask about the needle

        Returns:
            Dictionary with trial results including accuracy and latency
        """
        try:
            # Generate document with embedded needle
            doc = self.doc_generator.create_needle_haystack_document(
                haystack_words=self.haystack_words,
                needle=needle,
                position=position
            )

            # Query the model
            start_time = time.perf_counter()
            response = self.client.query(
                context=doc["content"],
                question=question
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Evaluate response
            # Extract expected answer from needle (assumes format "X is Y")
            expected_answer = needle.split(" is ")[-1] if " is " in needle else needle
            accuracy = evaluate_response(response, expected_answer, method="multi")

            # Count tokens
            token_count = count_tokens(doc["content"], model_name=self.model)

            logger.debug(
                f"Trial: position={position}, accuracy={accuracy:.2f}, "
                f"latency={latency_ms:.0f}ms, tokens={token_count}"
            )

            return {
                "position": position,
                "needle": needle,
                "question": question,
                "response": response,
                "expected_answer": expected_answer,
                "accuracy": accuracy,
                "latency_ms": latency_ms,
                "token_count": token_count,
                "haystack_words": doc["haystack_words"],
                "total_words": doc["total_words"],
                "error": None
            }

        except Exception as e:
            logger.error(f"Trial failed: {e}")
            return {
                "position": position,
                "needle": needle,
                "question": question,
                "response": None,
                "accuracy": 0.0,
                "latency_ms": 0.0,
                "token_count": 0,
                "error": str(e)
            }

    def run_full_experiment(
        self,
        num_runs: int = 10,
        positions: List[str] = None,
        use_different_facts: bool = True
    ) -> Dict[str, Any]:
        """Run complete Needle in Haystack experiment.

        Args:
            num_runs: Number of trials per position
            positions: Positions to test (default: ["start", "middle", "end"])
            use_different_facts: Whether to use different facts for each trial

        Returns:
            Dictionary with complete experiment results
        """
        if positions is None:
            positions = ["start", "middle", "end"]

        logger.info(
            f"Starting experiment with {num_runs} runs per position, "
            f"positions={positions}"
        )

        # Warmup
        logger.info("Warming up model...")
        self.client.warmup()

        all_trials = []
        experiment_start = time.perf_counter()

        # Predefined facts to use (rotating through them)
        facts = [
            ("The secret code is 7482", "What is the secret code?"),
            ("The magic number is 3.14159", "What is the magic number?"),
            ("The password is BlueSky2024", "What is the password?"),
            ("The treasure is buried at coordinates 42.7128, -73.0060", "Where is the treasure buried?"),
            ("The answer to the riddle is mirror", "What is the answer to the riddle?"),
            ("The winning lottery numbers are 7 14 21 35 42 49", "What are the winning lottery numbers?"),
            ("The vault combination is 12-34-56", "What is the vault combination?"),
            ("The WiFi password is SecureNet2024", "What is the WiFi password?"),
            ("The special ingredient is vanilla extract", "What is the special ingredient?"),
            ("The meeting time is 3:30 PM", "What time is the meeting?"),
        ]

        fact_idx = 0

        # Run trials for each position
        for position in positions:
            logger.info(f"Testing position: {position}")

            for run in range(num_runs):
                # Select fact
                if use_different_facts:
                    needle, question = facts[fact_idx % len(facts)]
                    fact_idx += 1
                else:
                    needle, question = facts[0]

                logger.info(f"  Run {run + 1}/{num_runs} for {position}")

                # Run trial
                trial_result = self.run_single_trial(
                    position=position,
                    needle=needle,
                    question=question
                )

                trial_result["trial_id"] = len(all_trials)
                trial_result["run_number"] = run
                all_trials.append(trial_result)

        total_runtime = time.perf_counter() - experiment_start

        # Organize results by position
        results_by_position = {pos: [] for pos in positions}
        for trial in all_trials:
            if trial["error"] is None:
                results_by_position[trial["position"]].append(trial["accuracy"])

        # Create result structure
        config = {
            "num_runs": num_runs,
            "positions": positions,
            "haystack_words": self.haystack_words,
            "model": self.model,
            "random_seed": self.random_seed,
            "use_different_facts": use_different_facts,
        }

        results = self.create_result_structure(
            trials=all_trials,
            config=config,
            total_runtime=total_runtime
        )

        # Add position-specific statistics
        results["position_results"] = results_by_position

        logger.info(
            f"Experiment completed in {total_runtime:.1f}s. "
            f"Success rate: {results['metadata']['success_rate']:.1%}"
        )

        return results

    def visualize_results(
        self,
        results: Dict[str, Any],
        output_dir: str
    ) -> None:
        """Generate visualization for experiment results.

        Args:
            results: Results from run_full_experiment()
            output_dir: Directory to save graphs
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        graph_path = output_path / "lost_in_middle.png"

        plot_lost_in_middle(
            results=results["position_results"],
            output_path=str(graph_path),
            show=False
        )

        logger.info(f"Saved visualization to {graph_path}")


# Convenience function for running experiment
def run_experiment(
    model: str = "llama2",
    num_runs: int = 10,
    output_dir: str = "./results/experiment1",
    random_seed: int = 42
) -> Dict[str, Any]:
    """Convenience function to run Experiment 1.

    Args:
        model: LLM model name
        num_runs: Number of trials per position
        output_dir: Output directory for results
        random_seed: Random seed

    Returns:
        Experiment results dictionary

    Example:
        >>> results = run_experiment(num_runs=5)
        >>> print(results["statistics"]["mean_accuracy"])
    """
    experiment = NeedleHaystackExperiment(
        model=model,
        random_seed=random_seed
    )

    results = experiment.run_full_experiment(num_runs=num_runs)
    experiment.save_results(results, output_dir)
    experiment.visualize_results(results, output_dir)

    return results
