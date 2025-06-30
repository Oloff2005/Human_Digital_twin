import argparse
import json
from pathlib import Path

from hdt.engine.run_simulator import run_simulator

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
DEFAULT_CONFIG = PACKAGE_ROOT / "config" / "units_config_active.yaml"
DEFAULT_INPUT = PROJECT_ROOT / "data" / "sample_inputs.json"


def _run_command(args: argparse.Namespace) -> None:
    """Execute the simulation and handle output."""
    results = run_simulator(
        config_path=str(args.config),
        input_path=str(DEFAULT_INPUT),
        steps=args.steps,
        verbose=False,
    )

    if args.log:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    else:
        print(json.dumps(results, indent=2))


def main(argv: list[str] | None = None) -> None:
    """Entry point for the HDT command line interface."""
    parser = argparse.ArgumentParser(prog="hdt", description="Human Digital Twin CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a simulation")
    run_parser.add_argument(
        "--steps",
        type=int,
        default=1,
        help="Number of simulation steps",
    )

    run_parser.add_argument(
        "--log",
        type=str,
        help="Optional path to write the simulation log",
    )
    run_parser.add_argument(
        "--config",
        type=str,
        default=str(DEFAULT_CONFIG),
        help="Path to unit configuration YAML",
    )
    run_parser.set_defaults(func=_run_command)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
