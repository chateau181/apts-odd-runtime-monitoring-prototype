from typing import Any

from src.models import InformationStatus, NormalizedRuntimeInformation

# configuration dictionary
# when a raw attribute is seen, how to explain it
INPUT_SPECIFICATIONS: dict[str, dict[str, Any]] = {
    "transport_type": {
        "entity": "Transport",
        "value_type": "categorical",
        "temporal_characteristic": "contextual",
    },
    "current_area": {
        "entity": "Environment",
        "value_type": "categorical",
        "temporal_characteristic": "contextual",
    },
    "vehicle_speed": {
        "entity": "APTS_Vehicle",
        "value_type": "number",
        "unit_key": "speed_unit",
        "expected_unit": "m/s",
        "temporal_characteristic": "dynamic",
    },
    "surface_condition": {
        "entity": "Environment",
        "value_type": "categorical",
        "temporal_characteristic": "dynamic",
        "optional": True,
    },
    "age": {
        "entity": "Patient",
        "value_type": "number",
        "unit": "years",
        "temporal_characteristic": "contextual",
    },
    "heart_rate": {
        "entity": "Patient",
        "value_type": "number",
        "unit_key": "heart_rate_unit",
        "expected_unit": "bpm",
        "temporal_characteristic": "dynamic",
    },
}


def _determine_information_status(
    value: Any,
    value_type: str,
) -> InformationStatus:
    if value is None:
        return InformationStatus.MISSING

    if value_type == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return InformationStatus.INVALID_UNUSABLE

    elif value_type == "categorical":
        if not isinstance(value, str) or not value.strip():
            return InformationStatus.INVALID_UNUSABLE

    else:
        raise ValueError(f"Unsupported value type: {value_type}")

    return InformationStatus.AVAILABLE


def normalize_runtime_snapshot(
    snapshot: dict[str, Any],
    cycle: int,
    source: str = "synthetic",
) -> list[NormalizedRuntimeInformation]:
    normalized_information = []

    for attribute, specification in INPUT_SPECIFICATIONS.items():
        if specification.get("optional", False) and attribute not in snapshot:
            continue

        value = snapshot.get(attribute)
        value_type = specification["value_type"]

        information_status = _determine_information_status(
            value=value,
            value_type=value_type,
        )

        unit = specification.get("unit")

        unit_key = specification.get("unit_key")
        if unit_key is not None:
            unit = snapshot.get(unit_key)

        expected_unit = specification.get("expected_unit")

        if (
                information_status == InformationStatus.AVAILABLE
                and expected_unit is not None
                and unit != expected_unit
        ):
            information_status = InformationStatus.INVALID_UNUSABLE

        information = NormalizedRuntimeInformation(
            attribute=attribute,
            entity=specification["entity"],
            value=value,
            value_type=value_type,
            unit=unit,
            source=source,
            temporal_characteristic=specification["temporal_characteristic"],
            cycle=cycle,
            information_status=information_status,
        )

        normalized_information.append(information)

    return normalized_information