from src.input_handler import normalize_runtime_snapshot
from src.models import InformationStatus, NormalizedRuntimeInformation
from src.scene_representation import build_scene_representation


def test_build_scene_representation():
    normalized_information = [
        NormalizedRuntimeInformation(
            attribute="vehicle_speed",
            entity="APTS_Vehicle",
            value=1.2,
            value_type="number",
            unit="m/s",
            temporal_characteristic="dynamic",
            cycle=1,
            information_status=InformationStatus.AVAILABLE,
        )
    ]

    result = build_scene_representation(normalized_information)

    assert len(result) == 1

    scene_element = result[0]

    assert scene_element.scene_element_id == "SE-VEHICLE_SPEED-01"
    assert scene_element.entity == "APTS_Vehicle"
    assert scene_element.attribute == "vehicle_speed"
    assert scene_element.value == 1.2
    assert scene_element.unit == "m/s"
    assert scene_element.information_status == InformationStatus.AVAILABLE
    assert scene_element.cycle == 1


def test_input_to_scene_integration():
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
        cycle=2,
    )

    scene_elements = build_scene_representation(
        normalized_information
    )

    assert len(scene_elements) == 6

    elements_by_attribute = {
        element.attribute: element
        for element in scene_elements
    }

    speed_element = elements_by_attribute["vehicle_speed"]
    heart_rate_element = elements_by_attribute["heart_rate"]
    surface_element = elements_by_attribute["surface_condition"]

    assert speed_element.value == 1.2
    assert speed_element.unit == "m/s"
    assert speed_element.scene_element_id == "SE-VEHICLE_SPEED-02"

    assert heart_rate_element.value == 85
    assert heart_rate_element.unit == "bpm"
    assert heart_rate_element.information_status == InformationStatus.AVAILABLE

    assert surface_element.value == "Wet"
    assert surface_element.entity == "Environment"


def test_missing_status_is_preserved_in_scene_element():
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
        normalized_information
    )

    heart_rate_element = next(
        element
        for element in scene_elements
        if element.attribute == "heart_rate"
    )

    assert heart_rate_element.value is None
    assert (
        heart_rate_element.information_status
        == InformationStatus.MISSING
    )
    assert heart_rate_element.scene_element_id == "SE-HEART_RATE-03"


def test_invalid_status_is_preserved_in_scene_element():
    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": "fast",
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    normalized_information = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=4,
    )

    scene_elements = build_scene_representation(
        normalized_information
    )

    speed_element = next(
        element
        for element in scene_elements
        if element.attribute == "vehicle_speed"
    )

    assert speed_element.value == "fast"
    assert (
        speed_element.information_status
        == InformationStatus.INVALID_UNUSABLE
    )
    assert speed_element.scene_element_id == "SE-VEHICLE_SPEED-04"