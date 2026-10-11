# integration test of input_handler, models, ontology_access, scene_representation and semantic_mapping

from src.input_handler import normalize_runtime_snapshot
from src.models import MappingStatus
from src.ontology_access import load_ontology
from src.scene_representation import build_scene_representation
from src.semantic_mapping import (
    load_mapping_specifications,
    map_scene_representation,
)


def test_runtime_snapshot_to_semantic_mapping():
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

    normalized_information = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=1,
    )

    scene_elements = build_scene_representation(
        normalized_information=normalized_information,
    )

    graph = load_ontology()
    specifications = load_mapping_specifications()

    mapping_results = map_scene_representation(
        scene_elements=scene_elements,
        specifications=specifications,
        graph=graph,
    )

    assert len(normalized_information) == 6
    assert len(scene_elements) == 6
    assert len(mapping_results) == 6

    assert all(
        result.mapping_status == MappingStatus.MAPPED
        for result in mapping_results
    )

    mapping_ids = {
        result.mapping_id
        for result in mapping_results
    }

    assert mapping_ids == {
        "M-01",
        "M-02",
        "M-03",
        "M-04",
        "M-05",
        "M-06",
    }