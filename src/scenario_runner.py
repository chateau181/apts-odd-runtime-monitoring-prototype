"""Execution of predefined runtime scenarios for the demonstrator.

The runner processes the scenario cycle by cycle using the already verified
monitoring core. Each cycle remains an independent snapshot evaluation while
the execution order is preserved for demonstration and traceability.
"""

from src.models import RuntimeScenario, ScenarioExecutionResult
from src.monitoring_pipeline import (
    MonitoringResources,
    run_monitoring_cycle_with_trace,
)


def run_runtime_scenario(
    scenario: RuntimeScenario,
    resources: MonitoringResources,
) -> ScenarioExecutionResult:
    """Execute all cycles of one predefined runtime scenario in order."""

    if not scenario.cycles:
        raise ValueError(
            "Runtime scenario must contain at least one cycle."
        )

    cycle_traces = [
        run_monitoring_cycle_with_trace(
            snapshot=scenario_cycle.snapshot,
            scenario_id=scenario.scenario_id,
            cycle=scenario_cycle.cycle,
            resources=resources,
        )
        for scenario_cycle in scenario.cycles
    ]

    return ScenarioExecutionResult(
        scenario_id=scenario.scenario_id,
        description=scenario.description,
        cycle_traces=cycle_traces,
    )