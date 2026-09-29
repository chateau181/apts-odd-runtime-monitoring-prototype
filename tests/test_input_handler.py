from src.input_handler import (
    _determine_information_status,
    normalize_runtime_snapshot,
)
from src.models import InformationStatus


def test_number_value_is_available():
    status = _determine_information_status(
        value=85,
        value_type="number",
    )

    assert status == InformationStatus.AVAILABLE


def test_none_value_is_missing():
    status = _determine_information_status(
        value=None,
        value_type="number",
    )

    assert status == InformationStatus.MISSING


def test_invalid_number_is_unusable():
    status = _determine_information_status(
        value="abc",
        value_type="number",
    )

    assert status == InformationStatus.INVALID_UNUSABLE


def test_valid_categorical_value_is_available():
    status = _determine_information_status(
        value="Wet",
        value_type="categorical",
    )

    assert status == InformationStatus.AVAILABLE


def test_boolean_is_not_accepted_as_number():
    status = _determine_information_status(
        value=True,
        value_type="number",
    )

    assert status == InformationStatus.INVALID_UNUSABLE


def test_unknown_categorical_value_is_still_available():
    status = _determine_information_status(
        value="Unsupported_surface_state",
        value_type="categorical",
    )

    assert status == InformationStatus.AVAILABLE


def test_normalize_complete_runtime_snapshot():
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

    result = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=1,
    )

    assert len(result) == 6

    speed_information = next(
        item for item in result if item.attribute == "vehicle_speed"
    )

    assert speed_information.entity == "APTS_Vehicle"
    assert speed_information.value == 1.2
    assert speed_information.unit == "m/s"
    assert speed_information.temporal_characteristic == "dynamic"
    assert speed_information.cycle == 1
    assert speed_information.information_status == InformationStatus.AVAILABLE


def test_missing_required_attribute_is_marked_missing():
    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate_unit": "bpm",
    }

    result = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=3,
    )

    heart_rate_information = next(
        item for item in result if item.attribute == "heart_rate"
    )

    assert heart_rate_information.value is None
    assert (
        heart_rate_information.information_status
        == InformationStatus.MISSING
    )
    assert heart_rate_information.cycle == 3


def test_absent_optional_surface_is_not_created():
    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    result = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=1,
    )

    attributes = [item.attribute for item in result]

    assert "surface_condition" not in attributes
    assert len(result) == 5


def test_explicitly_missing_surface_is_marked_missing():
    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "surface_condition": None,
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    result = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=1,
    )

    surface_information = next(
        item for item in result if item.attribute == "surface_condition"
    )

    assert surface_information.value is None
    assert (
        surface_information.information_status
        == InformationStatus.MISSING
    )


def test_missing_required_unit_is_unusable():
    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    result = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=1,
    )

    speed_information = next(
        item for item in result if item.attribute == "vehicle_speed"
    )

    assert (
        speed_information.information_status
        == InformationStatus.INVALID_UNUSABLE
    )


def test_unsupported_speed_unit_is_unusable():
    snapshot = {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "km/h",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm",
    }

    result = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=1,
    )

    speed_information = next(
        item for item in result if item.attribute == "vehicle_speed"
    )

    assert (
        speed_information.information_status
        == InformationStatus.INVALID_UNUSABLE
    )