"""CLI entry point for Route Guide System."""

import argparse
import sys
from pathlib import Path

from .orchestrator import RouteGuideOrchestrator
from .utils.config_loader import ConfigLoader
from .utils.logger import setup_logger, get_logger
from .utils.validators import validate_address, ValidationError


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Route Guide System - Enhance your journey with contextual content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main --source "New York, NY" --destination "Boston, MA"
  python -m src.main -s "San Francisco" -d "Los Angeles" --max-waypoints 10
  python -m src.main --source "Paris, France" --destination "Lyon, France" --config custom_config.yaml

For more information, see README.md
        """
    )

    parser.add_argument(
        "-s", "--source",
        required=True,
        help="Source address (origin)"
    )

    parser.add_argument(
        "-d", "--destination",
        required=True,
        help="Destination address"
    )

    parser.add_argument(
        "--max-waypoints",
        type=int,
        default=None,
        help="Maximum number of waypoints to process (default: from config)"
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom configuration file"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Override log level"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: auto-generated in results/)"
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save output to file"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Route Guide System v1.0.0"
    )

    return parser.parse_args()


def validate_inputs(args):
    """
    Validate command-line inputs.

    Args:
        args: Parsed arguments

    Raises:
        ValidationError: If validation fails
    """
    try:
        validate_address(args.source)
        validate_address(args.destination)

        if args.max_waypoints is not None:
            if args.max_waypoints < 1 or args.max_waypoints > 50:
                raise ValidationError(
                    "max-waypoints must be between 1 and 50"
                )

        if args.config and not Path(args.config).exists():
            raise ValidationError(f"Config file not found: {args.config}")

    except ValidationError as e:
        raise ValidationError(f"Invalid input: {e}")


def main():
    """Main entry point for CLI."""
    try:
        # Parse arguments
        args = parse_arguments()

        # Validate inputs
        validate_inputs(args)

        # Load configuration
        config = ConfigLoader(config_path=args.config) if args.config else ConfigLoader()

        # Override config with CLI arguments
        if args.log_level:
            import os
            os.environ["LOG_LEVEL"] = args.log_level

        if args.no_save:
            # Temporarily override config
            config.config["output"]["save_to_file"] = False

        if args.max_waypoints:
            config.config["route"]["max_waypoints"] = args.max_waypoints

        # Set up logging
        log_level = args.log_level or config.get_log_level()
        setup_logger(level=log_level)
        logger = get_logger(__name__)

        logger.info("=" * 60)
        logger.info("Route Guide System - Starting")
        logger.info("=" * 60)
        logger.info(f"Source: {args.source}")
        logger.info(f"Destination: {args.destination}")

        # Create orchestrator
        orchestrator = RouteGuideOrchestrator(config)

        # Process route
        logger.info("Processing route...")
        output = orchestrator.process_route(args.source, args.destination)

        # Print output
        print("\n" + "=" * 60)
        print("ROUTE GUIDE OUTPUT")
        print("=" * 60)
        print(output.to_json(pretty=True))
        print("=" * 60)

        # Print summary
        print(f"\nProcessed {len(output.stops)} stops")
        print(f"Total distance: {output.metadata['total_distance_km']} km")
        print(f"Estimated duration: {output.metadata['estimated_duration_minutes']} minutes")
        print(f"Processing time: {output.metadata['processing_time_seconds']} seconds")

        if not args.no_save:
            print(f"\nOutput saved to results/ directory")

        logger.info("Route Guide System - Complete")
        return 0

    except ValidationError as e:
        print(f"\n❌ Validation Error: {e}", file=sys.stderr)
        return 1

    except FileNotFoundError as e:
        print(f"\n❌ File Not Found: {e}", file=sys.stderr)
        print("\nMake sure you have:")
        print("  1. Created .env file from .env.example")
        print("  2. Set GOOGLE_MAPS_API_KEY in .env")
        print("  3. Installed all dependencies: pip install -r requirements.txt")
        return 1

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
