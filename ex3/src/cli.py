"""
Command-Line Interface

Provides CLI commands for:
- Turing Machine simulation
- Single translation
- Batch translation
- Analysis and visualization
"""

import os
import sys
import click
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from turing_machine import TuringMachine
from translation import ErrorInjector
from translation.claude_agent_runner import run_translation_pipeline
from evaluation import HuggingFaceEmbedding, EvaluationEngine
from analysis import GraphGenerator, StatisticsCalculator, ResultExporter


@click.group()
@click.version_option(version="1.0.0", prog_name="Translation & TM Simulator")
def cli():
    """
    Multi-Agent Translation Pipeline & Turing Machine Simulator

    A research tool for studying semantic drift in multi-hop translation
    and simulating classical Turing machines.
    """
    pass


@cli.command("turing-machine")
@click.option(
    "--config",
    required=True,
    type=click.Path(exists=True),
    help="Path to Turing machine configuration file (JSON/YAML)",
)
@click.option(
    "--tape", required=True, type=str, help="Initial tape content"
)
@click.option(
    "--max-steps",
    default=10000,
    type=int,
    help="Maximum number of steps to execute (default: 10000)",
)
@click.option(
    "--trace/--no-trace",
    default=False,
    help="Show execution trace (default: no)",
)
def turing_machine_cmd(config, tape, max_steps, trace):
    """
    Simulate a Turing Machine.

    Loads a TM configuration and executes it on the given tape.

    Example:
        my_tool turing-machine --config machines/unary_increment.json --tape "111" --max-steps 100
    """
    try:
        click.echo(f"Loading Turing Machine from: {config}")
        tm = TuringMachine.from_config_file(config)

        click.echo(f"Initial tape: {tape}")
        tm.load_tape(tape)

        click.echo(f"Running (max {max_steps} steps)...")
        result = tm.run(max_steps=max_steps, record_trace=trace)

        click.echo("\n" + "=" * 50)
        click.echo("RESULTS")
        click.echo("=" * 50)
        click.echo(f"Initial tape:  {result.initial_tape}")
        click.echo(f"Final tape:    {result.final_tape}")
        click.echo(f"Final state:   {result.final_state}")
        click.echo(f"Steps taken:   {result.steps_taken}")
        click.echo(f"Halted:        {result.halted}")

        if trace and result.trace:
            click.echo("\nExecution trace:")
            for step in result.trace[-10:]:  # Show last 10 steps
                click.echo(f"  {step}")

        if not result.halted:
            click.echo(
                "\nWarning: Machine did not reach a halting state",
                err=True,
            )
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("translate-once")
@click.option(
    "--sentence",
    required=True,
    type=str,
    help="English sentence to translate (minimum 15 words)",
)
@click.option(
    "--error-rate",
    default=0.0,
    type=float,
    help="Spelling error rate (0.0 to 1.0, default: 0.0)",
)
@click.option(
    "--seed", default=42, type=int, help="Random seed for reproducibility (default: 42)"
)
@click.option(
    "--output",
    type=click.Path(),
    help="Optional: Save results to JSON file",
)
def translate_once_cmd(sentence, error_rate, seed, output):
    """
    Translate a single sentence through the pipeline.

    Translates: English → French → Hebrew → English
    Uses Claude CLI agents defined in src/agents/*.md files

    Example:
        my_tool translate-once --sentence "Your sentence here" --error-rate 0.30
    """
    try:
        # Validate inputs
        word_count = len(sentence.split())
        if word_count < 15:
            click.echo(
                f"Error: Sentence must contain at least 15 words (got {word_count})",
                err=True,
            )
            sys.exit(1)

        if not 0.0 <= error_rate <= 1.0:
            click.echo(f"Error: Error rate must be between 0.0 and 1.0", err=True)
            sys.exit(1)

        click.echo("Initializing translation pipeline...")

        # Get agent file paths
        src_dir = Path(__file__).parent
        agent_files = [
            src_dir / "agents" / "en_to_fr.md",
            src_dir / "agents" / "fr_to_he.md",
            src_dir / "agents" / "he_to_en.md",
        ]

        # Verify agent files exist
        for agent_file in agent_files:
            if not agent_file.exists():
                click.echo(f"Error: Agent file not found: {agent_file}", err=True)
                sys.exit(1)

        click.echo(f"Original: {sentence}")
        click.echo(f"Error rate: {error_rate * 100}%")
        click.echo(f"Seed: {seed}\n")

        # Inject errors if needed
        text_to_translate = sentence
        if error_rate > 0:
            injector = ErrorInjector(seed=seed)
            text_to_translate = injector.inject_errors(sentence, error_rate)
            click.echo(f"Corrupted: {text_to_translate}\n")

        # Run translation pipeline
        click.echo("Running translation pipeline...")
        translations = run_translation_pipeline(
            text_to_translate,
            [str(f) for f in agent_files],
            timeout=120,
        )

        translation_fr, translation_he, translation_en = translations

        click.echo("\n" + "=" * 70)
        click.echo("TRANSLATION RESULTS")
        click.echo("=" * 70)
        click.echo(f"Original (EN):  {sentence}")
        if error_rate > 0:
            click.echo(f"Corrupted (EN): {text_to_translate}")
        click.echo(f"French:         {translation_fr}")
        click.echo(f"Hebrew:         {translation_he}")
        click.echo(f"Final (EN):     {translation_en}")

        # Compute semantic distance using HuggingFace embeddings
        click.echo("\nComputing semantic distance (using HuggingFace embeddings)...")
        embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        embedding_provider = HuggingFaceEmbedding(model_name=embedding_model)
        eval_engine = EvaluationEngine(embedding_provider)

        eval_result = eval_engine.evaluate(
            sentence, translation_en, error_rate=error_rate
        )

        click.echo(f"\nCosine distance:    {eval_result.cosine_distance:.6f}")
        click.echo(f"Euclidean distance: {eval_result.euclidean_distance:.6f}")

        # Save results if requested
        if output:
            data = [
                {
                    "original": sentence,
                    "corrupted": text_to_translate,
                    "error_rate": error_rate,
                    "translation_fr": translation_fr,
                    "translation_he": translation_he,
                    "translation_en": translation_en,
                    "cosine_distance": eval_result.cosine_distance,
                    "euclidean_distance": eval_result.euclidean_distance,
                    "word_count": word_count,
                    "seed": seed,
                }
            ]
            ResultExporter.export_json(data, output)
            click.echo(f"\nResults saved to: {output}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("translate-batch")
@click.option(
    "--sentence",
    required=True,
    type=str,
    help="Base English sentence to translate (minimum 15 words)",
)
@click.option(
    "--min-error", default=0.0, type=float, help="Minimum error rate (default: 0.0)"
)
@click.option(
    "--max-error", default=0.5, type=float, help="Maximum error rate (default: 0.5)"
)
@click.option(
    "--steps", default=11, type=int, help="Number of error rate steps (default: 11)"
)
@click.option(
    "--seed", default=42, type=int, help="Random seed for reproducibility (default: 42)"
)
@click.option(
    "--output-dir",
    default="results",
    type=click.Path(),
    help="Directory to save results (default: results/)",
)
def translate_batch_cmd(sentence, min_error, max_error, steps, seed, output_dir):
    """
    Translate a sentence with varying error rates (batch processing).

    Runs multiple translations with different error rates to analyze
    the relationship between errors and semantic drift.

    Example:
        my_tool translate-batch --sentence "Your sentence here" --steps 11
    """
    try:
        # Validate inputs
        word_count = len(sentence.split())
        if word_count < 15:
            click.echo(
                f"Error: Sentence must contain at least 15 words (got {word_count})",
                err=True,
            )
            sys.exit(1)

        # Create output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        click.echo("Initializing batch translation...")
        click.echo(f"Error range: {min_error * 100}% to {max_error * 100}%")
        click.echo(f"Steps: {steps}")
        click.echo(f"Sentence: {sentence}\n")

        # Get agent file paths
        src_dir = Path(__file__).parent
        agent_files = [
            str(src_dir / "agents" / "en_to_fr.md"),
            str(src_dir / "agents" / "fr_to_he.md"),
            str(src_dir / "agents" / "he_to_en.md"),
        ]

        # Create embedding provider and evaluation engine (HuggingFace)
        embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        embedding_provider = HuggingFaceEmbedding(model_name=embedding_model)
        eval_engine = EvaluationEngine(embedding_provider)

        # Generate error rates
        import numpy as np

        error_rates = np.linspace(min_error, max_error, steps).tolist()

        # Batch processing
        results = []
        with click.progressbar(error_rates, label="Processing") as bar:
            for error_rate in bar:
                # Inject errors
                text_to_translate = sentence
                if error_rate > 0:
                    injector = ErrorInjector(seed=seed + int(error_rate * 1000))
                    text_to_translate = injector.inject_errors(sentence, error_rate)

                # Run translation pipeline
                translations = run_translation_pipeline(
                    text_to_translate,
                    agent_files,
                    timeout=120,
                )

                translation_fr, translation_he, translation_en = translations

                # Evaluate
                eval_result = eval_engine.evaluate(
                    sentence,
                    translation_en,
                    error_rate=error_rate,
                )

                results.append(
                    {
                        "original": sentence,
                        "corrupted": text_to_translate,
                        "error_rate": error_rate,
                        "translation_fr": translation_fr,
                        "translation_he": translation_he,
                        "translation_en": translation_en,
                        "cosine_distance": eval_result.cosine_distance,
                        "euclidean_distance": eval_result.euclidean_distance,
                        "word_count": word_count,
                    }
                )

        # Export results
        csv_path = output_dir / "batch_results.csv"
        json_path = output_dir / "batch_results.json"

        ResultExporter.export_csv(results, str(csv_path))
        ResultExporter.export_json(results, str(json_path))

        click.echo(f"\n✓ Results saved:")
        click.echo(f"  CSV:  {csv_path}")
        click.echo(f"  JSON: {json_path}")

        # Calculate and show statistics
        error_rates_list = [r["error_rate"] for r in results]
        distances = [r["cosine_distance"] for r in results]

        stats_calc = StatisticsCalculator()
        trend = stats_calc.calculate_trend(error_rates_list, distances)

        click.echo(f"\n📊 Statistics:")
        click.echo(f"  Correlation: {trend.correlation:.4f}")
        click.echo(f"  R²: {trend.r_squared:.4f}")
        click.echo(f"  Trend: y = {trend.slope:.4f}x + {trend.intercept:.4f}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("analyze")
@click.option(
    "--input",
    required=True,
    type=click.Path(exists=True),
    help="Path to results JSON file (from translate-batch)",
)
@click.option(
    "--output",
    default="results/graphs/analysis.png",
    type=click.Path(),
    help="Path to save the graph (default: results/graphs/analysis.png)",
)
@click.option(
    "--dpi", default=300, type=int, help="Graph resolution in DPI (default: 300)"
)
def analyze_cmd(input, output, dpi):
    """
    Analyze results and generate visualization.

    Creates a scatter plot showing the relationship between
    error rate and semantic distance.

    Example:
        my_tool analyze --input results/batch_results.json --output graph.png
    """
    try:
        import json

        click.echo(f"Loading results from: {input}")

        # Load results
        with open(input, "r") as f:
            data = json.load(f)

        results = data.get("results", data)  # Handle both formats

        if not results:
            click.echo("Error: No results found in input file", err=True)
            sys.exit(1)

        # Extract data
        error_rates = [r["error_rate"] for r in results]
        cosine_distances = [r["cosine_distance"] for r in results]
        euclidean_distances = [r["euclidean_distance"] for r in results]

        click.echo(f"Loaded {len(results)} data points")

        # Calculate statistics
        stats_calc = StatisticsCalculator()
        trend = stats_calc.calculate_trend(error_rates, cosine_distances)

        click.echo(f"\nStatistics:")
        click.echo(f"  Correlation: {trend.correlation:.4f}")
        click.echo(f"  R² score: {trend.r_squared:.4f}")
        click.echo(f"  Trend line: y = {trend.slope:.4f}x + {trend.intercept:.4f}")

        # Generate graph
        click.echo(f"\nGenerating graph...")
        graph_gen = GraphGenerator()

        graph_gen.generate_scatter_plot(
            error_rates=error_rates,
            distances=cosine_distances,
            output_path=output,
            title="Semantic Drift vs. Spelling Error Rate",
            xlabel="Spelling Error Rate",
            ylabel="Cosine Distance",
            show_trend=True,
            dpi=dpi,
        )

        click.echo(f"✓ Graph saved to: {output}")

        # Also generate multi-metric plot
        multi_output = Path(output).parent / "multi_metric_analysis.png"
        graph_gen.generate_multi_metric_plot(
            error_rates=error_rates,
            cosine_distances=cosine_distances,
            euclidean_distances=euclidean_distances,
            output_path=str(multi_output),
            dpi=dpi,
        )

        click.echo(f"✓ Multi-metric graph saved to: {multi_output}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
