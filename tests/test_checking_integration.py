from src.checking import (
    evaluate_checking_conditions,
    load_checking_conditions,
)
from src.input_handler import normalize_runtime_snapshot
from src.models import ConditionStatus
from src.ontology_access import load_ontology
from src.scene_representation import build_scene_representation
from src.semantic_mapping import (
    load_mapping_specifications,
    map_scene_representation,
)


def test_normal_runtime_snapshot_reaches_satisfied_conditions():
    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    normalized_information = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=1,
    )

    scene_elements = build_scene_representation(
        normalized_information=normalized_information,
    )

    graph = load_ontology()
    mapping_specifications = load_mapping_specifications()

    mapping_results = map_scene_representation(
        scene_elements=scene_elements,
        specifications=mapping_specifications,
        graph=graph,
    )

    checking_conditions = load_checking_conditions()

    condition_results = evaluate_checking_conditions(
        conditions=checking_conditions,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    result_by_condition_id = {
        result.condition_id: result
        for result in condition_results
    }

    assert len(condition_results) == 2

    assert (
        result_by_condition_id["A-01"].condition_status
        == ConditionStatus.SATISFIED
    )
    assert (
        result_by_condition_id["A-03"].condition_status
        == ConditionStatus.SATISFIED
    )

    assert "A-02" not in result_by_condition_id

def test_unmappable_surface_reaches_unresolved_condition():
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

    normalized_information = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=1,
    )

    scene_elements = build_scene_representation(
        normalized_information=normalized_information,
    )

    graph = load_ontology()
    mapping_specifications = load_mapping_specifications()

    mapping_results = map_scene_representation(
        scene_elements=scene_elements,
        specifications=mapping_specifications,
        graph=graph,
    )

    checking_conditions = load_checking_conditions()

    condition_results = evaluate_checking_conditions(
        conditions=checking_conditions,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    result_by_condition_id = {
        result.condition_id: result
        for result in condition_results
    }

    assert (
        result_by_condition_id["A-01"].condition_status
        == ConditionStatus.SATISFIED
    )

    assert (
        result_by_condition_id["A-02"].condition_status
        == ConditionStatus.UNRESOLVED
    )

    assert (
        result_by_condition_id["A-03"].condition_status
        == ConditionStatus.SATISFIED
    )

    assert "Unmappable" in result_by_condition_id["A-02"].reason

def test_mixed_runtime_snapshot_preserves_all_condition_states():
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

    normalized_information = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=1,
    )

    scene_elements = build_scene_representation(
        normalized_information=normalized_information,
    )

    graph = load_ontology()
    mapping_specifications = load_mapping_specifications()

    mapping_results = map_scene_representation(
        scene_elements=scene_elements,
        specifications=mapping_specifications,
        graph=graph,
    )

    checking_conditions = load_checking_conditions()

    condition_results = evaluate_checking_conditions(
        conditions=checking_conditions,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    result_by_condition_id = {
        result.condition_id: result
        for result in condition_results
    }

    assert (
        result_by_condition_id["A-01"].condition_status
        == ConditionStatus.UNRESOLVED
    )

    assert (
        result_by_condition_id["A-02"].condition_status
        == ConditionStatus.VIOLATED
    )

    assert (
        result_by_condition_id["A-03"].condition_status
        == ConditionStatus.SATISFIED
    )