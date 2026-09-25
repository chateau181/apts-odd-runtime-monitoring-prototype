from src.models import (
    AssessmentState,
    CheckingCondition,
    ConditionOperator,
    ConditionResult,
    ConditionStatus,
    InformationStatus,
    MappingResult,
    MappingSpecification,
    MappingStatus,
    MappingType,
    MonitoringResult,
    NormalizedRuntimeInformation,
    ResponseType,
    SceneElement,
)


def test_information_status_values():
    assert InformationStatus.AVAILABLE.value == "Available"
    assert InformationStatus.MISSING.value == "Missing"
    assert InformationStatus.INCONSISTENT.value == "Inconsistent"
    assert InformationStatus.OUTDATED.value == "Outdated"
    assert InformationStatus.INVALID_UNUSABLE.value == "Invalid / Unusable"


def test_mapping_status_values():
    assert MappingStatus.MAPPED.value == "Mapped"
    assert MappingStatus.UNMAPPABLE.value == "Unmappable"


def test_condition_status_values():
    assert ConditionStatus.SATISFIED.value == "Satisfied"
    assert ConditionStatus.VIOLATED.value == "Violated"
    assert ConditionStatus.UNRESOLVED.value == "Unresolved"


def test_assessment_state_values():
    assert AssessmentState.INSIDE_ODD.value == "Inside ODD"
    assert AssessmentState.OUTSIDE_ODD.value == "Outside ODD"
    assert AssessmentState.UNCLEAR.value == "Unclear"


def test_response_type_values():
    assert ResponseType.NONE.value == "None"
    assert ResponseType.INTERVENTION.value == "Intervention"
    assert ResponseType.REVIEW.value == "Review"
    assert ResponseType.CLARIFICATION.value == "Clarification"


def test_mapping_type_values():
    assert MappingType.DIRECT.value == "Direct"
    assert MappingType.STRUCTURED.value == "Structured / context-dependent"
    assert MappingType.EXTENSION_SUPPORTED.value == "Extension-supported"


def test_normalized_runtime_information_creation():
    info = NormalizedRuntimeInformation(
        attribute="vehicle_speed",
        entity="APTS_Vehicle",
        value=1.2,
        value_type="number",
        unit="m/s",
        temporal_characteristic="dynamic",
    )

    assert info.attribute == "vehicle_speed"
    assert info.value == 1.2
    assert info.unit == "m/s"
    assert info.information_status == InformationStatus.AVAILABLE


def test_scene_element_creation():
    element = SceneElement(
        scene_element_id="SE-SPEED-01",
        entity="APTS_Vehicle",
        attribute="vehicle_speed",
        value=1.2,
        value_type="number",
        information_status=InformationStatus.AVAILABLE,
        unit="m/s",
        temporal_characteristic="dynamic",
    )

    assert element.scene_element_id == "SE-SPEED-01"
    assert element.attribute == "vehicle_speed"
    assert element.value == 1.2
    assert element.information_status == InformationStatus.AVAILABLE


def test_mapping_specification_creation():
    specification = MappingSpecification(
        mapping_id="M-03",
        scene_attribute="surface_condition",
        scene_value="Wet",
        ontology_reference="Wet",
        ontology_element_type="NamedIndividual",
        mapping_type=MappingType.DIRECT,
    )

    assert specification.mapping_id == "M-03"
    assert specification.scene_value == "Wet"
    assert specification.ontology_reference == "Wet"
    assert specification.mapping_type == MappingType.DIRECT
    assert specification.supporting_ontology_references == {}


def test_mapped_result_creation():
    result = MappingResult(
        scene_element_id="SE-SURFACE-01",
        mapping_status=MappingStatus.MAPPED,
        mapping_id="M-03",
        ontology_reference="Wet",
        ontology_element_type="NamedIndividual",
        mapping_type=MappingType.DIRECT,
    )

    assert result.scene_element_id == "SE-SURFACE-01"
    assert result.mapping_status == MappingStatus.MAPPED
    assert result.ontology_reference == "Wet"
    assert result.reason is None


def test_checking_condition_creation():
    condition = CheckingCondition(
        condition_id="A-03",
        name="Maximum vehicle speed",
        checked_attribute="vehicle_speed",
        required_attributes=("vehicle_speed",),
        operator=ConditionOperator.LESS_EQUAL,
        unit="m/s",
        maximum=1.5,
    )

    assert condition.condition_id == "A-03"
    assert condition.checked_attribute == "vehicle_speed"
    assert condition.operator == ConditionOperator.LESS_EQUAL
    assert condition.maximum == 1.5
    assert condition.applicability_context == {}


def test_condition_result_creation():
    result = ConditionResult(
        condition_id="A-03",
        condition_status=ConditionStatus.VIOLATED,
        checked_attribute="vehicle_speed",
        observed_value=1.6,
        related_scene_element_ids=["SE-SPEED-01"],
        ontology_reference="speedValue",
    )

    assert result.condition_id == "A-03"
    assert result.condition_status == ConditionStatus.VIOLATED
    assert result.observed_value == 1.6
    assert result.related_scene_element_ids == ["SE-SPEED-01"]


def test_monitoring_result_creation():
    condition_result = ConditionResult(
        condition_id="A-03",
        condition_status=ConditionStatus.VIOLATED,
        checked_attribute="vehicle_speed",
        observed_value=1.6,
    )

    result = MonitoringResult(
        scenario_id="DS-01",
        cycle=2,
        assessment=AssessmentState.OUTSIDE_ODD,
        response=ResponseType.INTERVENTION,
        condition_results=[condition_result],
    )

    assert result.scenario_id == "DS-01"
    assert result.cycle == 2
    assert result.assessment == AssessmentState.OUTSIDE_ODD
    assert len(result.condition_results) == 1


def test_unmappable_result_creation():
    result = MappingResult(
        scene_element_id="SE-SURFACE-02",
        mapping_status=MappingStatus.UNMAPPABLE,
        reason="No sufficient predefined ontology correspondence.",
    )

    assert result.mapping_status == MappingStatus.UNMAPPABLE
    assert result.mapping_id is None
    assert result.ontology_reference is None
    assert result.reason == "No sufficient predefined ontology correspondence."


def test_condition_operator_values():
    assert ConditionOperator.RANGE_INCLUSIVE.value == "Range inclusive"
    assert ConditionOperator.LESS_EQUAL.value == "Less than or equal"
    assert ConditionOperator.PROHIBITED_STATE.value == "Prohibited state"