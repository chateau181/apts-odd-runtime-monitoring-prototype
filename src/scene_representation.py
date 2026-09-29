from src.models import NormalizedRuntimeInformation, SceneElement


def _build_scene_element_id(
    attribute: str,
    cycle: int | None,
) -> str:
    attribute_part = attribute.upper()

    if cycle is None:
        return f"SE-{attribute_part}"

    return f"SE-{attribute_part}-{cycle:02d}"


def build_scene_representation(
    normalized_information: list[NormalizedRuntimeInformation],
) -> list[SceneElement]:
    scene_elements = []

    for information in normalized_information:
        scene_element = SceneElement(
            scene_element_id=_build_scene_element_id(
                attribute=information.attribute,
                cycle=information.cycle,
            ),
            entity=information.entity,
            attribute=information.attribute,
            value=information.value,
            value_type=information.value_type,
            information_status=information.information_status,
            unit=information.unit,
            source=information.source,
            temporal_characteristic=information.temporal_characteristic,
            cycle=information.cycle,
        )

        scene_elements.append(scene_element)

    return scene_elements