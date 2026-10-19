from src.demonstrator_output import (
    format_cycle_trace,
    format_scenario_execution,
    format_scenario_summary,
)
from src.monitoring_pipeline import load_monitoring_resources
from src.scenario_loader import load_runtime_scenario
from src.scenario_runner import run_runtime_scenario


def test_format_scenario_execution_contains_scenario_header():
    scenario = load_runtime_scenario()
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    output = format_scenario_execution(execution)

    assert "Scenario Execution: DS-01" in output
    assert "Cycles: 5" in output

def test_format_cycle_two_shows_speed_violation():
    scenario = load_runtime_scenario()
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    output = format_cycle_trace(
        execution.cycle_traces[1]
    )

    assert "Cycle: 2" in output
    assert "vehicle_speed = 1.6 m/s" in output
    assert "speedValue" in output
    assert "A-03: Violated" in output
    assert "Assessment: Outside ODD" in output
    assert "Primary Response: Intervention" in output

def test_format_cycle_three_shows_unresolved_information():
    scenario = load_runtime_scenario()
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    output = format_cycle_trace(
        execution.cycle_traces[2]
    )

    assert "Cycle: 3" in output
    assert "heart_rate = <missing>" in output
    assert "A-01: Unresolved" in output
    assert "Assessment: Unclear" in output
    assert "Primary Response: Clarification" in output

def test_format_scenario_summary_contains_all_cycles():
    scenario = load_runtime_scenario()
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    summary = format_scenario_summary(execution)

    assert "Scenario Summary" in summary
    assert "A-01" in summary
    assert "A-02" in summary
    assert "A-03" in summary

    for cycle in range(1, 6):
        assert str(cycle) in summary

def test_format_scenario_summary_preserves_condition_states():
        scenario = load_runtime_scenario()
        resources = load_monitoring_resources()

        execution = run_runtime_scenario(
            scenario=scenario,
            resources=resources,
        )

        summary = format_scenario_summary(execution)

        assert "N/A" in summary
        assert "Unresolved" in summary
        assert "Violated" in summary
        assert "Inside ODD" in summary
        assert "Outside ODD" in summary
        assert "Unclear" in summary