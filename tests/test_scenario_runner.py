from pathlib import Path

from src.models import (
    AssessmentState,
    ConditionStatus,
    ResponseType,
)
from src.monitoring_pipeline import load_monitoring_resources
from src.scenario_loader import load_runtime_scenario
from src.scenario_runner import run_runtime_scenario


def test_run_dynamic_scenario_preserves_all_cycles():
    scenario = load_runtime_scenario()
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    assert execution.scenario_id == "DS-01"
    assert len(execution.cycle_traces) == 5

    assert [
        trace.cycle
        for trace in execution.cycle_traces
    ] == [1, 2, 3, 4, 5]

def test_dynamic_scenario_produces_expected_assessment_sequence():
    scenario = load_runtime_scenario()
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    assessments = [
        trace.monitoring_result.assessment
        for trace in execution.cycle_traces
    ]

    assert assessments == [
        AssessmentState.INSIDE_ODD,
        AssessmentState.OUTSIDE_ODD,
        AssessmentState.UNCLEAR,
        AssessmentState.OUTSIDE_ODD,
        AssessmentState.INSIDE_ODD,
    ]

def test_dynamic_scenario_produces_expected_response_sequence():
    scenario = load_runtime_scenario()
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    responses = [
        trace.monitoring_result.response
        for trace in execution.cycle_traces
    ]

    assert responses == [
        ResponseType.NONE,
        ResponseType.INTERVENTION,
        ResponseType.CLARIFICATION,
        ResponseType.INTERVENTION,
        ResponseType.NONE,
    ]

def test_dynamic_scenario_preserves_key_condition_results():
    scenario = load_runtime_scenario()
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    cycle_three = execution.cycle_traces[2]
    cycle_four = execution.cycle_traces[3]

    cycle_three_results = {
        result.condition_id: result
        for result in cycle_three.condition_results
    }

    cycle_four_results = {
        result.condition_id: result
        for result in cycle_four.condition_results
    }

    assert (
        cycle_three_results["A-01"].condition_status
        == ConditionStatus.UNRESOLVED
    )

    assert (
        cycle_four_results["A-02"].condition_status
        == ConditionStatus.VIOLATED
    )

def test_unmappable_edge_case_results_in_unclear():
    scenario = load_runtime_scenario(
        Path("data/scenarios/ec_unmappable.json")
    )
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    trace = execution.cycle_traces[0]

    results = {
        result.condition_id: result
        for result in trace.condition_results
    }

    assert (
        results["A-02"].condition_status
        == ConditionStatus.UNRESOLVED
    )

    assert (
        trace.monitoring_result.assessment
        == AssessmentState.UNCLEAR
    )

    assert (
        trace.monitoring_result.response
        == ResponseType.CLARIFICATION
    )

def test_mixed_edge_case_preserves_violation_and_uncertainty():
    scenario = load_runtime_scenario(
        Path("data/scenarios/ec_mixed.json")
    )
    resources = load_monitoring_resources()

    execution = run_runtime_scenario(
        scenario=scenario,
        resources=resources,
    )

    trace = execution.cycle_traces[0]

    results = {
        result.condition_id: result
        for result in trace.condition_results
    }

    assert (
        results["A-01"].condition_status
        == ConditionStatus.UNRESOLVED
    )

    assert (
        results["A-02"].condition_status
        == ConditionStatus.VIOLATED
    )

    assert (
        results["A-03"].condition_status
        == ConditionStatus.SATISFIED
    )

    assert (
        trace.monitoring_result.assessment
        == AssessmentState.OUTSIDE_ODD
    )

    assert (
        trace.monitoring_result.response
        == ResponseType.INTERVENTION
    )