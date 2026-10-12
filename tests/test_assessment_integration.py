from src.assessment import determine_assessment_state
from src.checking import (
    evaluate_checking_conditions,
    load_checking_conditions,
)
from src.input_handler import normalize_runtime_snapshot
from src.models import AssessmentState
from src.ontology_access import load_ontology
from src.scene_representation import build_scene_representation
from src.semantic_mapping import (
    load_mapping_specifications,
    map_scene_representation,
)


def test_nominal_snapshot_produces_inside_odd():
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

    assessment = determine_assessment_state(
        condition_results=condition_results,
    )

    assert assessment == AssessmentState.INSIDE_ODD

def test_speed_violation_produces_outside_odd():
    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.6,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    normalized_information = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=2,
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

    assessment = determine_assessment_state(
        condition_results=condition_results,
    )

    assert assessment == AssessmentState.OUTSIDE_ODD

def test_missing_heart_rate_produces_unclear():
    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": None,
        "heart_rate_unit": "bpm",
    }

    normalized_information = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=3,
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

    assessment = determine_assessment_state(
        condition_results=condition_results,
    )

    assert assessment == AssessmentState.UNCLEAR

def test_violation_takes_precedence_in_mixed_runtime_snapshot():
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
        cycle=4,
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

    assessment = determine_assessment_state(
        condition_results=condition_results,
    )

    assert assessment == AssessmentState.OUTSIDE_ODD