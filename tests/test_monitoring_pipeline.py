from src.models import (
    AssessmentState,
    ConditionStatus,
    ResponseType,
)
from src.monitoring_pipeline import (
    load_monitoring_resources,
    run_monitoring_cycle,
    run_monitoring_cycle_with_trace,
)


def test_end_to_end_inside_odd_cycle():
    resources = load_monitoring_resources()

    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    result = run_monitoring_cycle(
        snapshot=snapshot,
        scenario_id="DS-01",
        cycle=1,
        resources=resources,
    )

    assert result.assessment == AssessmentState.INSIDE_ODD
    assert result.response == ResponseType.NONE
    assert result.scenario_id == "DS-01"
    assert result.cycle == 1

def test_end_to_end_speed_violation_cycle():
    resources = load_monitoring_resources()

    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.6,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    result = run_monitoring_cycle(
        snapshot=snapshot,
        scenario_id="DS-01",
        cycle=2,
        resources=resources,
    )

    assert result.assessment == AssessmentState.OUTSIDE_ODD
    assert result.response == ResponseType.INTERVENTION

    assert any(
        condition.condition_id == "A-03"
        and condition.condition_status == ConditionStatus.VIOLATED
        for condition in result.condition_results
    )

def test_end_to_end_missing_heart_rate_cycle():
    resources = load_monitoring_resources()

    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": None,
        "heart_rate_unit": "bpm",
    }

    result = run_monitoring_cycle(
        snapshot=snapshot,
        scenario_id="DS-01",
        cycle=3,
        resources=resources,
    )

    assert result.assessment == AssessmentState.UNCLEAR
    assert result.response == ResponseType.CLARIFICATION

    assert any(
        condition.condition_id == "A-01"
        and condition.condition_status == ConditionStatus.UNRESOLVED
        for condition in result.condition_results
    )

def test_end_to_end_wet_surface_cycle():
    resources = load_monitoring_resources()

    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "surface_condition": "Wet",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    result = run_monitoring_cycle(
        snapshot=snapshot,
        scenario_id="DS-01",
        cycle=4,
        resources=resources,
    )

    assert result.assessment == AssessmentState.OUTSIDE_ODD
    assert result.response == ResponseType.INTERVENTION

    assert any(
        condition.condition_id == "A-02"
        and condition.condition_status == ConditionStatus.VIOLATED
        for condition in result.condition_results
    )

def test_end_to_end_unmappable_surface_cycle():
    resources = load_monitoring_resources()

    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "surface_condition": "Unsupported_surface_state",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    result = run_monitoring_cycle(
        snapshot=snapshot,
        scenario_id="EC-Unmappable",
        cycle=1,
        resources=resources,
    )

    assert result.assessment == AssessmentState.UNCLEAR
    assert result.response == ResponseType.CLARIFICATION

    assert any(
        condition.condition_id == "A-02"
        and condition.condition_status == ConditionStatus.UNRESOLVED
        for condition in result.condition_results
    )

def test_end_to_end_mixed_cycle_preserves_unresolved_evidence():
    resources = load_monitoring_resources()

    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "surface_condition": "Wet",
        "age": 45,
        "heart_rate": None,
        "heart_rate_unit": "bpm",
    }

    result = run_monitoring_cycle(
        snapshot=snapshot,
        scenario_id="EC-Mixed",
        cycle=1,
        resources=resources,
    )

    assert result.assessment == AssessmentState.OUTSIDE_ODD
    assert result.response == ResponseType.INTERVENTION

    result_by_condition_id = {
        condition.condition_id: condition
        for condition in result.condition_results
    }

    assert (
        result_by_condition_id["A-01"].condition_status
        == ConditionStatus.UNRESOLVED
    )

    assert (
        result_by_condition_id["A-02"].condition_status
        == ConditionStatus.VIOLATED
    )

def test_end_to_end_heart_rate_violation_uses_review():
    resources = load_monitoring_resources()

    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 110,
        "heart_rate_unit": "bpm",
    }

    result = run_monitoring_cycle(
        snapshot=snapshot,
        scenario_id="EC-HeartRate",
        cycle=1,
        resources=resources,
    )

    assert result.assessment == AssessmentState.OUTSIDE_ODD
    assert result.response == ResponseType.REVIEW

    assert any(
        condition.condition_id == "A-01"
        and condition.condition_status == ConditionStatus.VIOLATED
        for condition in result.condition_results
    )

def test_end_to_end_trace_preserves_all_processing_stages():
    resources = load_monitoring_resources()

    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    trace = run_monitoring_cycle_with_trace(
        snapshot=snapshot,
        scenario_id="DS-01",
        cycle=1,
        resources=resources,
    )

    assert trace.scenario_id == "DS-01"
    assert trace.cycle == 1
    assert trace.raw_snapshot == snapshot

    assert trace.normalized_information
    assert trace.scene_elements
    assert trace.mapping_results
    assert trace.condition_results

    assert (
        trace.monitoring_result.assessment
        == AssessmentState.INSIDE_ODD
    )
    assert trace.monitoring_result.response == ResponseType.NONE

def test_trace_links_vehicle_speed_through_mapping_and_checking():
    resources = load_monitoring_resources()

    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.6,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    trace = run_monitoring_cycle_with_trace(
        snapshot=snapshot,
        scenario_id="DS-01",
        cycle=2,
        resources=resources,
    )

    speed_scene_element = next(
        element
        for element in trace.scene_elements
        if element.attribute == "vehicle_speed"
    )

    speed_mapping = next(
        mapping
        for mapping in trace.mapping_results
        if mapping.scene_element_id
        == speed_scene_element.scene_element_id
    )

    speed_condition = next(
        condition
        for condition in trace.condition_results
        if condition.condition_id == "A-03"
    )

    assert speed_scene_element.value == 1.6
    assert speed_mapping.ontology_reference == "speedValue"
    assert speed_condition.condition_status == ConditionStatus.VIOLATED

    assert (
        trace.monitoring_result.assessment
        == AssessmentState.OUTSIDE_ODD
    )