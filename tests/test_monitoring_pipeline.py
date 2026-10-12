from src.models import (
    AssessmentState,
    ConditionStatus,
    ResponseType,
)
from src.monitoring_pipeline import (
    load_monitoring_resources,
    run_monitoring_cycle,
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