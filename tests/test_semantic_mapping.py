from src.models import InformationStatus, MappingStatus, MappingType, SceneElement
from src.ontology_access import load_ontology
from src.semantic_mapping import (
    find_mapping_specification,
    load_mapping_specifications,
    map_scene_element,
    map_scene_representation,
)


def test_load_mapping_specifications():
    specifications = load_mapping_specifications()

    assert len(specifications) == 6

    wet_mapping = next(
        specification
        for specification in specifications
        if specification.mapping_id == "M-03"
    )

    assert wet_mapping.scene_attribute == "surface_condition"
    assert wet_mapping.scene_value == "Wet"
    assert wet_mapping.ontology_reference == "Wet"
    assert wet_mapping.ontology_element_type == "NamedIndividual"
    assert wet_mapping.mapping_type == MappingType.DIRECT

def test_load_structured_mapping_specification():
    specifications = load_mapping_specifications()

    age_mapping = next(
        specification
        for specification in specifications
        if specification.mapping_id == "M-04"
    )

    assert age_mapping.scene_entity == "Patient"
    assert age_mapping.ontology_reference == "Age_scalar"
    assert age_mapping.mapping_type == MappingType.STRUCTURED
    assert age_mapping.supporting_ontology_references == {
        "relation": "hasAge",
        "value_property": "ageValue",
    }

def test_find_direct_mapping_for_wet():
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-SURFACE_CONDITION-01",
        entity="Environment",
        attribute="surface_condition",
        value="Wet",
        value_type="categorical",
        information_status=InformationStatus.AVAILABLE,
        temporal_characteristic="dynamic",
        cycle=1,
    )

    specification = find_mapping_specification(
        scene_element=scene_element,
        specifications=specifications,
    )

    assert specification is not None
    assert specification.mapping_id == "M-03"

def test_no_mapping_specification_for_unsupported_surface():
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-SURFACE_CONDITION-01",
        entity="Environment",
        attribute="surface_condition",
        value="Unsupported_surface_state",
        value_type="categorical",
        information_status=InformationStatus.AVAILABLE,
        temporal_characteristic="dynamic",
        cycle=1,
    )

    specification = find_mapping_specification(
        scene_element=scene_element,
        specifications=specifications,
    )

    assert specification is None

def test_find_structured_mapping_for_vehicle_speed():
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-VEHICLE_SPEED-01",
        entity="APTS_Vehicle",
        attribute="vehicle_speed",
        value=1.6,
        value_type="number",
        information_status=InformationStatus.AVAILABLE,
        unit="m/s",
        temporal_characteristic="dynamic",
        cycle=1,
    )

    specification = find_mapping_specification(
        scene_element=scene_element,
        specifications=specifications,
    )

    assert specification is not None
    assert specification.mapping_id == "M-05"
    assert specification.mapping_type == MappingType.STRUCTURED

def test_map_wet_scene_element():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-SURFACE_CONDITION-01",
        entity="Environment",
        attribute="surface_condition",
        value="Wet",
        value_type="categorical",
        information_status=InformationStatus.AVAILABLE,
        temporal_characteristic="dynamic",
        cycle=1,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_status == MappingStatus.MAPPED
    assert result.mapping_id == "M-03"
    assert result.ontology_reference == "Wet"
    assert result.ontology_element_type == "NamedIndividual"
    assert result.mapping_type == MappingType.DIRECT

def test_map_unsupported_surface_as_unmappable():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-SURFACE_CONDITION-01",
        entity="Environment",
        attribute="surface_condition",
        value="Unsupported_surface_state",
        value_type="categorical",
        information_status=InformationStatus.AVAILABLE,
        temporal_characteristic="dynamic",
        cycle=1,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_status == MappingStatus.UNMAPPABLE
    assert result.mapping_id is None
    assert result.ontology_reference is None

def test_missing_information_is_not_mapped():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-HEART_RATE-03",
        entity="Patient",
        attribute="heart_rate",
        value=None,
        value_type="number",
        information_status=InformationStatus.MISSING,
        unit="bpm",
        temporal_characteristic="dynamic",
        cycle=3,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is None

def test_structured_speed_mapping_preserves_runtime_context():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-VEHICLE_SPEED-02",
        entity="APTS_Vehicle",
        attribute="vehicle_speed",
        value=1.6,
        value_type="number",
        information_status=InformationStatus.AVAILABLE,
        unit="m/s",
        temporal_characteristic="dynamic",
        cycle=2,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_status == MappingStatus.MAPPED
    assert result.mapping_id == "M-05"
    assert result.ontology_reference == "speedValue"

    assert result.mapping_context == {
        "scene_entity": "APTS_Vehicle",
        "runtime_value": 1.6,
        "unit": "m/s",
    }

def test_structured_age_mapping_preserves_supporting_references():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-AGE-01",
        entity="Patient",
        attribute="age",
        value=45,
        value_type="number",
        information_status=InformationStatus.AVAILABLE,
        unit="years",
        temporal_characteristic="contextual",
        cycle=1,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_status == MappingStatus.MAPPED
    assert result.mapping_id == "M-04"
    assert result.ontology_reference == "Age_scalar"

    assert result.mapping_context[
        "supporting_ontology_references"
    ] == {
        "relation": "hasAge",
        "value_property": "ageValue",
    }

def test_direct_mapping_has_empty_mapping_context():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-SURFACE_CONDITION-01",
        entity="Environment",
        attribute="surface_condition",
        value="Wet",
        value_type="categorical",
        information_status=InformationStatus.AVAILABLE,
        temporal_characteristic="dynamic",
        cycle=1,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_context == {}

def test_age_mapping_with_existing_supporting_references_is_mapped():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-AGE-01",
        entity="Patient",
        attribute="age",
        value=45,
        value_type="number",
        information_status=InformationStatus.AVAILABLE,
        unit="years",
        temporal_characteristic="contextual",
        cycle=1,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_status == MappingStatus.MAPPED
    assert result.mapping_id == "M-04"

def test_missing_supporting_reference_makes_mapping_unmappable():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    age_mapping = next(
        specification
        for specification in specifications
        if specification.mapping_id == "M-04"
    )

    age_mapping.supporting_ontology_references[
        "relation"
    ] = "DefinitelyMissingRelation"

    scene_element = SceneElement(
        scene_element_id="SE-AGE-01",
        entity="Patient",
        attribute="age",
        value=45,
        value_type="number",
        information_status=InformationStatus.AVAILABLE,
        unit="years",
        temporal_characteristic="contextual",
        cycle=1,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_status == MappingStatus.UNMAPPABLE
    assert result.mapping_id == "M-04"
    assert result.ontology_reference is None
    assert "DefinitelyMissingRelation" in result.reason

def test_wet_mapping_has_matching_ontology_type():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-SURFACE_CONDITION-01",
        entity="Environment",
        attribute="surface_condition",
        value="Wet",
        value_type="categorical",
        information_status=InformationStatus.AVAILABLE,
        temporal_characteristic="dynamic",
        cycle=1,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_status == MappingStatus.MAPPED
    assert result.ontology_element_type == "NamedIndividual"

def test_heart_rate_mapping_accepts_existing_rdf_predicate():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_element = SceneElement(
        scene_element_id="SE-HEART_RATE-01",
        entity="Patient",
        attribute="heart_rate",
        value=85,
        value_type="number",
        information_status=InformationStatus.AVAILABLE,
        unit="bpm",
        temporal_characteristic="dynamic",
        cycle=1,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_status == MappingStatus.MAPPED
    assert result.mapping_id == "M-06"
    assert result.ontology_reference == "hasHeartFrequency"
    assert result.ontology_element_type == "RDFPredicate"

def test_wrong_expected_ontology_type_is_unmappable():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    wet_mapping = next(
        specification
        for specification in specifications
        if specification.mapping_id == "M-03"
    )

    wet_mapping.ontology_element_type = "Class"

    scene_element = SceneElement(
        scene_element_id="SE-SURFACE_CONDITION-01",
        entity="Environment",
        attribute="surface_condition",
        value="Wet",
        value_type="categorical",
        information_status=InformationStatus.AVAILABLE,
        temporal_characteristic="dynamic",
        cycle=1,
    )

    result = map_scene_element(
        scene_element=scene_element,
        specifications=specifications,
        graph=graph,
    )

    assert result is not None
    assert result.mapping_status == MappingStatus.UNMAPPABLE
    assert result.mapping_id == "M-03"

def test_map_complete_scene_representation():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_elements = [
        SceneElement(
            scene_element_id="SE-TRANSPORT_TYPE-01",
            entity="Transport",
            attribute="transport_type",
            value="Patient_transport",
            value_type="categorical",
            information_status=InformationStatus.AVAILABLE,
            temporal_characteristic="contextual",
            cycle=1,
        ),
        SceneElement(
            scene_element_id="SE-CURRENT_AREA-01",
            entity="Environment",
            attribute="current_area",
            value="Corridor",
            value_type="categorical",
            information_status=InformationStatus.AVAILABLE,
            temporal_characteristic="contextual",
            cycle=1,
        ),
        SceneElement(
            scene_element_id="SE-VEHICLE_SPEED-01",
            entity="APTS_Vehicle",
            attribute="vehicle_speed",
            value=1.2,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="m/s",
            temporal_characteristic="dynamic",
            cycle=1,
        ),
        SceneElement(
            scene_element_id="SE-AGE-01",
            entity="Patient",
            attribute="age",
            value=45,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="years",
            temporal_characteristic="contextual",
            cycle=1,
        ),
        SceneElement(
            scene_element_id="SE-HEART_RATE-01",
            entity="Patient",
            attribute="heart_rate",
            value=85,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="bpm",
            temporal_characteristic="dynamic",
            cycle=1,
        ),
    ]

    results = map_scene_representation(
        scene_elements=scene_elements,
        specifications=specifications,
        graph=graph,
    )

    assert len(results) == 5
    assert all(
        result.mapping_status == MappingStatus.MAPPED
        for result in results
    )

def test_scene_mapping_skips_unavailable_information():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_elements = [
        SceneElement(
            scene_element_id="SE-VEHICLE_SPEED-03",
            entity="APTS_Vehicle",
            attribute="vehicle_speed",
            value=1.2,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="m/s",
            temporal_characteristic="dynamic",
            cycle=3,
        ),
        SceneElement(
            scene_element_id="SE-HEART_RATE-03",
            entity="Patient",
            attribute="heart_rate",
            value=None,
            value_type="number",
            information_status=InformationStatus.MISSING,
            unit="bpm",
            temporal_characteristic="dynamic",
            cycle=3,
        ),
    ]

    results = map_scene_representation(
        scene_elements=scene_elements,
        specifications=specifications,
        graph=graph,
    )

    assert len(results) == 1
    assert results[0].mapping_id == "M-05"

def test_scene_mapping_preserves_unmappable_result():
    graph = load_ontology()
    specifications = load_mapping_specifications()

    scene_elements = [
        SceneElement(
            scene_element_id="SE-VEHICLE_SPEED-01",
            entity="APTS_Vehicle",
            attribute="vehicle_speed",
            value=1.2,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="m/s",
            temporal_characteristic="dynamic",
            cycle=1,
        ),
        SceneElement(
            scene_element_id="SE-SURFACE_CONDITION-01",
            entity="Environment",
            attribute="surface_condition",
            value="Unsupported_surface_state",
            value_type="categorical",
            information_status=InformationStatus.AVAILABLE,
            temporal_characteristic="dynamic",
            cycle=1,
        ),
    ]

    results = map_scene_representation(
        scene_elements=scene_elements,
        specifications=specifications,
        graph=graph,
    )

    assert len(results) == 2

    result_by_element_id = {
        result.scene_element_id: result
        for result in results
    }

    assert (
        result_by_element_id["SE-VEHICLE_SPEED-01"].mapping_status
        == MappingStatus.MAPPED
    )

    assert (
        result_by_element_id["SE-SURFACE_CONDITION-01"].mapping_status
        == MappingStatus.UNMAPPABLE
    )