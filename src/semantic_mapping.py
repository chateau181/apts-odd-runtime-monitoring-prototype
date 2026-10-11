"""Semantic mapping from runtime Scene Elements to ontology references.

This module applies predefined MappingSpecifications to available Scene
Elements and verifies the referenced ontology elements against the original
read-only ontology.

Semantic mapping only determines whether a usable Scene Element can be
associated with a predefined ontology reference. It does not evaluate ODD
conditions or determine Inside / Outside / Unclear assessments.
"""
import json
from pathlib import Path

from rdflib import Graph

from src.models import (
    InformationStatus,
    MappingResult,
    MappingSpecification,
    MappingStatus,
    MappingType,
    SceneElement,
)
from src.ontology_access import (
    get_ontology_element_type,
    ontology_element_exists,
    ontology_element_is_predicate,
)

DEFAULT_MAPPING_DEFINITIONS_PATH = Path(
    "data/config/mapping_definitions.json"
)


def load_mapping_specifications(
    mapping_path: Path = DEFAULT_MAPPING_DEFINITIONS_PATH,
) -> list[MappingSpecification]:
    """Load pre-runtime mapping definitions from JSON configuration."""
    with mapping_path.open("r", encoding="utf-8") as file:
        raw_definitions = json.load(file)

    specifications = []

    for definition in raw_definitions:
        specification = MappingSpecification(
            mapping_id=definition["mapping_id"], #[]for necessary
            scene_attribute=definition["scene_attribute"],
            ontology_reference=definition["ontology_reference"],
            ontology_element_type=definition["ontology_element_type"],
            mapping_type=MappingType(definition["mapping_type"]),
            scene_entity=definition.get("scene_entity"), #.get() for optional
            scene_value=definition.get("scene_value"),
            supporting_ontology_references=definition.get(
                "supporting_ontology_references",
                {},
            ),
        )

        specifications.append(specification)

    return specifications

def find_mapping_specification(
    scene_element: SceneElement,
    specifications: list[MappingSpecification],
) -> MappingSpecification | None:
    """Find the predefined mapping rule applicable to one Scene Element."""
    for specification in specifications:
        # Attribute matching is mandatory. Entity and value act as additional
        # constraints only when they are explicitly defined by the specification.
        if specification.scene_attribute != scene_element.attribute:
            continue

        if (
            specification.scene_entity is not None
            and specification.scene_entity != scene_element.entity
        ):
            continue

        if (
            specification.scene_value is not None
            and specification.scene_value != scene_element.value
        ):
            continue

        return specification

    return None

def _find_missing_supporting_references(
    graph: Graph,
    specification: MappingSpecification,
) -> list[str]:
    """Return configured supporting ontology references that cannot be found."""
    # Structured mappings may rely on additional ontology elements besides
    # their primary semantic reference, for example hasAge and ageValue.
    # for M-04 Age
    return [
        reference
        for reference in specification.supporting_ontology_references.values()
        if not ontology_element_exists(graph, reference)
    ]

def _build_mapping_context(  #for M-04 M-05 & M-06
    scene_element: SceneElement,
    specification: MappingSpecification,
) -> dict[str, object]:
    """Preserve runtime context needed by structured mappings."""
    # Runtime values remain part of the Scene Representation. They are recorded
    # here for traceability and are not written into the ontology.
    if specification.mapping_type != MappingType.STRUCTURED:
        return {}

    context = {
        "scene_entity": scene_element.entity,
        "runtime_value": scene_element.value,
    }

    if scene_element.unit is not None:
        context["unit"] = scene_element.unit

    if specification.supporting_ontology_references:
        context["supporting_ontology_references"] = (
            specification.supporting_ontology_references
        )

    return context

def map_scene_element(
    scene_element: SceneElement,
    specifications: list[MappingSpecification],
    graph: Graph,
) -> MappingResult | None:
    """Map one usable Scene Element to a verified ontology reference."""
    # Missing, inconsistent, outdated, or otherwise unusable information is an
    # information-quality problem, not a semantic-mapping failure. Therefore,
    # no Unmappable result is created for unavailable information.
    if scene_element.information_status != InformationStatus.AVAILABLE:
        return None

    specification = find_mapping_specification(
        scene_element=scene_element,
        specifications=specifications,
    )

    # An Available Scene Element becomes Unmappable when no predefined semantic
    # correspondence exists for its attribute/entity/value combination.
    if specification is None:
        return MappingResult(
            scene_element_id=scene_element.scene_element_id,
            mapping_status=MappingStatus.UNMAPPABLE,
            reason="No predefined mapping specification matched the Scene Element.",
        )

    if not ontology_element_exists(
        graph,
        specification.ontology_reference,
    ):
        return MappingResult(
            scene_element_id=scene_element.scene_element_id,
            mapping_status=MappingStatus.UNMAPPABLE,
            mapping_id=specification.mapping_id,
            reason="The predefined ontology reference does not exist.",
        )

    if not _ontology_type_matches_specification(
            graph=graph,
            specification=specification,
    ):
        return MappingResult(
            scene_element_id=scene_element.scene_element_id,
            mapping_status=MappingStatus.UNMAPPABLE,
            mapping_id=specification.mapping_id,
            reason=(
                "The ontology reference does not match the expected "
                "ontology element type."
            ),
        )

    missing_supporting_references = _find_missing_supporting_references(
        graph=graph,
        specification=specification,
    )

    if missing_supporting_references:
        return MappingResult(
            scene_element_id=scene_element.scene_element_id,
            mapping_status=MappingStatus.UNMAPPABLE,
            mapping_id=specification.mapping_id,
            reason=(
                    "One or more supporting ontology references do not exist: "
                    + ", ".join(missing_supporting_references)
            ),
        )

    # A configured mapping is accepted only if its ontology reference is
    # actually present in the frozen ontology baseline.
    return MappingResult(
        scene_element_id=scene_element.scene_element_id,
        mapping_status=MappingStatus.MAPPED,
        mapping_id=specification.mapping_id,
        ontology_reference=specification.ontology_reference,
        ontology_element_type=specification.ontology_element_type,
        mapping_type=specification.mapping_type,
        mapping_context=_build_mapping_context(
            scene_element=scene_element,
            specification=specification,
        ),
    )

def _ontology_type_matches_specification(
    graph: Graph,
    specification: MappingSpecification,
) -> bool:
    # "RDFPredicate" is a prototype-level descriptive label, not a formal
    # rdf:type found in the ontology. It is used for hasHeartFrequency because
    # that URI occurs as a predicate but has no explicit OWL property type.
    if specification.ontology_element_type == "RDFPredicate":
        return ontology_element_is_predicate(
            graph,
            specification.ontology_reference,
        )

    actual_type = get_ontology_element_type( # for M-01 to M-05
        graph,
        specification.ontology_reference,
    )

    return actual_type == specification.ontology_element_type

def map_scene_representation(
    scene_elements: list[SceneElement],
    specifications: list[MappingSpecification],
    graph: Graph,
) -> list[MappingResult]:
    """Apply semantic mapping to all usable elements of one scene snapshot."""
    mapping_results = []

    for scene_element in scene_elements:
        result = map_scene_element(
            scene_element=scene_element,
            specifications=specifications,
            graph=graph,
        )
        # map_scene_element() returns None for unavailable information. Such
        # elements remain in the Scene Representation but have no MappingResult.
        if result is not None:
            mapping_results.append(result)

    return mapping_results