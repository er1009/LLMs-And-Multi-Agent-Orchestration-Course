#!/usr/bin/env python
"""Main entry point for Context Windows Lab experiments.

This script provides a CLI interface to run all experiments
or individual experiments with customizable parameters.
"""

import argparse
import logging
import sys
from pathlib import Path

from src.experiments import (
    experiment1_needle_haystack,
    experiment2_context_size,
    experiment3_rag_comparison,
    experiment4_strategies
)
from src.config.settings import config


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.

    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create logs directory
    if config.log_file:
        Path(config.log_file).parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(config.log_file) if config.log_file else logging.NullHandler()
        ]
    )


def run_experiment_1(args) -> None:
    """Run Experiment 1: Needle in Haystack."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 1: NEEDLE IN HAYSTACK (LOST IN THE MIDDLE)")
    print("=" * 70 + "\n")

    output_dir = Path(args.output_dir) / "experiment1"

    results = experiment1_needle_haystack.run_experiment(
        model=args.model,
        num_runs=args.num_runs,
        output_dir=str(output_dir),
        random_seed=args.seed
    )

    print("\n📊 Results Summary:")
    print(f"  Mean Accuracy: {results['statistics']['mean_accuracy']:.2%}")
    print(f"  Std Accuracy: {results['statistics']['std_accuracy']:.2%}")
    print(f"  Runtime: {results['metadata']['total_runtime_seconds']:.1f}s")
    print(f"\n  Results saved to: {output_dir}")


def run_experiment_2(args) -> None:
    """Run Experiment 2: Context Size Impact."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: CONTEXT WINDOW SIZE IMPACT")
    print("=" * 70 + "\n")

    output_dir = Path(args.output_dir) / "experiment2"

    results = experiment2_context_size.run_experiment(
        model=args.model,
        num_runs=args.num_runs,
        output_dir=str(output_dir),
        random_seed=args.seed
    )

    print("\n📊 Results Summary:")
    print(f"  Mean Accuracy: {results['statistics']['mean_accuracy']:.2%}")
    print(f"  Mean Latency: {results['statistics']['mean_latency']:.0f}ms")
    print(f"  Runtime: {results['metadata']['total_runtime_seconds']:.1f}s")
    print(f"\n  Results saved to: {output_dir}")


def run_experiment_3(args) -> None:
    """Run Experiment 3: RAG vs Full Context."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: RAG VS FULL CONTEXT COMPARISON")
    print("=" * 70 + "\n")

    output_dir = Path(args.output_dir) / "experiment3"

    results = experiment3_rag_comparison.run_experiment(
        model=args.model,
        num_runs=args.num_runs,
        output_dir=str(output_dir),
        random_seed=args.seed
    )

    agg = results["aggregated"]
    print("\n📊 Results Summary:")
    print(f"  RAG Accuracy: {agg['rag']['accuracy']:.2%}")
    print(f"  Full Context Accuracy: {agg['full']['accuracy']:.2%}")
    print(f"  RAG Latency: {agg['rag']['latency']:.0f}ms")
    print(f"  Full Context Latency: {agg['full']['latency']:.0f}ms")
    print(f"  RAG Tokens: {agg['rag']['tokens']:.0f}")
    print(f"  Full Context Tokens: {agg['full']['tokens']:.0f}")
    print(f"  Runtime: {results['metadata']['total_runtime_seconds']:.1f}s")
    print(f"\n  Results saved to: {output_dir}")


def run_experiment_4(args) -> None:
    """Run Experiment 4: Context Engineering Strategies."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: CONTEXT ENGINEERING STRATEGIES")
    print("=" * 70 + "\n")

    output_dir = Path(args.output_dir) / "experiment4"

    num_actions = args.num_actions if hasattr(args, 'num_actions') else 10

    results = experiment4_strategies.run_experiment(
        model=args.model,
        num_actions=num_actions,
        output_dir=str(output_dir),
        random_seed=args.seed
    )

    print("\n📊 Results Summary:")
    print(f"  Mean Accuracy: {results['statistics']['mean_accuracy']:.2%}")
    print(f"  Mean Latency: {results['statistics']['mean_latency']:.0f}ms")
    print(f"  Runtime: {results['metadata']['total_runtime_seconds']:.1f}s")
    print(f"\n  Results saved to: {output_dir}")


def run_all_experiments(args) -> None:
    """Run all experiments sequentially."""
    print("\n" + "=" * 70)
    print("RUNNING ALL EXPERIMENTS")
    print("=" * 70 + "\n")

    experiments = [
        ("Experiment 1", run_experiment_1),
        ("Experiment 2", run_experiment_2),
        ("Experiment 3", run_experiment_3),
        ("Experiment 4", run_experiment_4),
    ]

    for name, func in experiments:
        try:
            func(args)
        except KeyboardInterrupt:
            print(f"\n⚠️  {name} interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ {name} failed: {e}")
            logging.exception(f"{name} failed")
            if not args.continue_on_error:
                sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ ALL EXPERIMENTS COMPLETED")
    print("=" * 70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Context Windows Lab - LLM Performance Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all experiments
  python main.py --all

  # Run specific experiment
  python main.py --experiment 1

  # Run with custom parameters
  python main.py --experiment 1 --num-runs 20 --model mistral

  # Run with verbose logging
  python main.py --all --verbose
        """
    )

    # Experiment selection
    exp_group = parser.add_mutually_exclusive_group(required=True)
    exp_group.add_argument(
        "--all",
        action="store_true",
        help="Run all experiments sequentially"
    )
    exp_group.add_argument(
        "--experiment", "-e",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run specific experiment (1-4)"
    )

    # Common parameters
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=config.ollama_model,
        help=f"Ollama model to use (default: {config.ollama_model})"
    )
    parser.add_argument(
        "--num-runs", "-n",
        type=int,
        default=config.default_num_runs,
        help=f"Number of trials per test (default: {config.default_num_runs})"
    )
    parser.add_argument(
        "--num-actions",
        type=int,
        default=10,
        help="Number of actions for Experiment 4 (default: 10)"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=config.random_seed,
        help=f"Random seed for reproducibility (default: {config.random_seed})"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default=config.results_dir,
        help=f"Output directory for results (default: {config.results_dir})"
    )

    # Execution options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging"
    )
    parser.add_argument(
        "--skip-viz",
        action="store_true",
        help="Skip visualization generation"
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue with next experiment if one fails (only with --all)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("Starting Context Windows Lab")
    logger.info(f"Configuration: model={args.model}, num_runs={args.num_runs}, seed={args.seed}")

    # Check output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Results will be saved to: {output_path}")

    # Run experiments
    try:
        if args.all:
            run_all_experiments(args)
        else:
            experiment_map = {
                1: run_experiment_1,
                2: run_experiment_2,
                3: run_experiment_3,
                4: run_experiment_4,
            }
            experiment_map[args.experiment](args)

        print("\n✨ Done! Check the results directory for outputs.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Fatal error occurred")
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
