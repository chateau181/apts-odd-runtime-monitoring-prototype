"""Command-line entry point for the minimal prototype demonstrator.

The module loads a predefined runtime scenario and the monitoring resources,
executes all scenario cycles, and prints the resulting execution trace.
"""

import argparse
from pathlib import Path

from src.demonstrator_output import format_scenario_execution
from src.monitoring_pipeline import load_monitoring_resources
from src.scenario_loader import load_runtime_scenario
from src.scenario_runner import run_runtime_scenario

SCENARIO_PATHS: dict[str, Path] = {
    "ds-01": Path("data/scenarios/ds_01_dynamic.json"),
    "ec-unmappable": Path("data/scenarios/ec_unmappable.json"),
    "ec-mixed": Path("data/scenarios/ec_mixed.json"),
}


def parse_arguments(
    argv: list[str] | None = None,
) -> argparse.Namespace:
    """Parse command-line arguments for the demonstrator."""

    parser = argparse.ArgumentParser(
        description="Run the APTS ODD monitoring demonstrator."
    )

    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIO_PATHS),
        default="ds-01",
        help="Predefined runtime scenario to execute.",
    )

    return parser.parse_args(argv)


def main(
    argv: list[str] | None = None,
) -> None:
    """Run one selected predefined scenario."""

    args = parse_arguments(argv)

    scenario = load_runtime_scenario(
        SCENARIO_PATHS[args.scenario]
    )
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    output = format_scenario_execution(execution)

    print(output)


if __name__ == "__main__":
    main()