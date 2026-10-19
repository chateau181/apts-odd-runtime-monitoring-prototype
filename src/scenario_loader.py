"""Loading of predefined runtime scenarios for the demonstrator.

Scenario files remain external JSON inputs. This module converts their
structure into typed Python scenario objects without performing input
normalization or monitoring logic.
"""

import json
from pathlib import Path

from src.models import RuntimeScenario, ScenarioCycle

DEFAULT_SCENARIO_PATH = Path(
    "data/scenarios/ds_01_dynamic.json"
)


def load_runtime_scenario(
    scenario_path: Path = DEFAULT_SCENARIO_PATH,
) -> RuntimeScenario:
    """Load one external scenario JSON file into structured Python objects."""

    with scenario_path.open("r", encoding="utf-8") as file:
        raw_scenario = json.load(file)

    cycles = [
        ScenarioCycle(
            cycle=raw_cycle["cycle"],
            snapshot=raw_cycle["snapshot"],
        )
        for raw_cycle in raw_scenario["cycles"]
    ]

    return RuntimeScenario(
        scenario_id=raw_scenario["scenario_id"],
        description=raw_scenario["description"],
        cycles=cycles,
    )