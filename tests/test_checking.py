from src.checking import (
    check_condition,
    check_required_information,
    check_required_mappings,
    determine_condition_applicability,
    evaluate_checking_conditions,
    evaluate_condition_operator,
    load_checking_conditions,
)
from src.models import (
    ConditionOperator,
    ConditionStatus,
    InformationStatus,
    MappingResult,
    MappingStatus,
    SceneElement,
)


def test_load_checking_conditions():
    conditions = load_checking_conditions()

    assert len(conditions) == 3

    heart_rate_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-01"
    )

    assert heart_rate_condition.checked_attribute == "heart_rate"
    assert heart_rate_condition.required_attributes == (
        "heart_rate",
        "age",
    )
    assert (
        heart_rate_condition.operator
        == ConditionOperator.RANGE_INCLUSIVE
    )
    assert heart_rate_condition.minimum == 60
    assert heart_rate_condition.maximum == 100
    assert heart_rate_condition.unit == "bpm"

def test_load_optional_surface_condition():
    conditions = load_checking_conditions()

    surface_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-02"
    )

    assert surface_condition.checked_attribute == "surface_condition"
    assert surface_condition.activation_attribute == "surface_condition"
    assert (
        surface_condition.operator
        == ConditionOperator.PROHIBITED_STATE
    )
    assert surface_condition.prohibited_state == "Wet"

def test_load_speed_condition():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

    assert speed_condition.checked_attribute == "vehicle_speed"
    assert speed_condition.operator == ConditionOperator.LESS_EQUAL
    assert speed_condition.maximum == 1.5
    assert speed_condition.unit == "m/s"

def test_condition_is_applicable_in_patient_transport_context():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

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
        )
    ]

    applicability = determine_condition_applicability(
        condition=speed_condition,
        scene_elements=scene_elements,
    )

    assert applicability is True

def test_condition_is_not_applicable_in_different_transport_context():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-TRANSPORT_TYPE-01",
            entity="Transport",
            attribute="transport_type",
            value="Other_transport",
            value_type="categorical",
            information_status=InformationStatus.AVAILABLE,
            temporal_characteristic="contextual",
            cycle=1,
        )
    ]

    applicability = determine_condition_applicability(
        condition=speed_condition,
        scene_elements=scene_elements,
    )

    assert applicability is False

def test_condition_applicability_is_unknown_when_context_is_missing():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-TRANSPORT_TYPE-01",
            entity="Transport",
            attribute="transport_type",
            value=None,
            value_type="categorical",
            information_status=InformationStatus.MISSING,
            temporal_characteristic="contextual",
            cycle=1,
        )
    ]

    applicability = determine_condition_applicability(
        condition=speed_condition,
        scene_elements=scene_elements,
    )

    assert applicability is None

def test_surface_condition_is_not_applicable_when_activation_attribute_absent():
    conditions = load_checking_conditions()

    surface_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-02"
    )

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
        )
    ]

    applicability = determine_condition_applicability(
        condition=surface_condition,
        scene_elements=scene_elements,
    )

    assert applicability is False

def test_surface_condition_is_applicable_when_present_but_missing():
    conditions = load_checking_conditions()

    surface_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-02"
    )

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
            scene_element_id="SE-SURFACE_CONDITION-01",
            entity="Environment",
            attribute="surface_condition",
            value=None,
            value_type="categorical",
            information_status=InformationStatus.MISSING,
            temporal_characteristic="dynamic",
            cycle=1,
        ),
    ]

    applicability = determine_condition_applicability(
        condition=surface_condition,
        scene_elements=scene_elements,
    )

    assert applicability is True

def test_missing_heart_rate_makes_required_information_unresolved():
    conditions = load_checking_conditions()

    heart_rate_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-01"
    )

    scene_elements = [
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
        SceneElement(
            scene_element_id="SE-AGE-03",
            entity="Patient",
            attribute="age",
            value=45,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="years",
            temporal_characteristic="contextual",
            cycle=3,
        ),
    ]

    result = check_required_information(
        condition=heart_rate_condition,
        scene_elements=scene_elements,
    )

    assert result is not None
    assert result.condition_status == ConditionStatus.UNRESOLVED
    assert result.observed_value is None
    assert "heart_rate" in result.reason
    assert "Missing" in result.reason

def test_missing_age_makes_heart_rate_condition_unresolved():
    conditions = load_checking_conditions()

    heart_rate_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-01"
    )

    scene_elements = [
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
        SceneElement(
            scene_element_id="SE-AGE-01",
            entity="Patient",
            attribute="age",
            value=None,
            value_type="number",
            information_status=InformationStatus.MISSING,
            unit="years",
            temporal_characteristic="contextual",
            cycle=1,
        ),
    ]

    result = check_required_information(
        condition=heart_rate_condition,
        scene_elements=scene_elements,
    )

    assert result is not None
    assert result.condition_status == ConditionStatus.UNRESOLVED
    assert result.observed_value == 85
    assert "age" in result.reason

def test_invalid_speed_makes_required_information_unresolved():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-VEHICLE_SPEED-01",
            entity="APTS_Vehicle",
            attribute="vehicle_speed",
            value="fast",
            value_type="number",
            information_status=InformationStatus.INVALID_UNUSABLE,
            unit="m/s",
            temporal_characteristic="dynamic",
            cycle=1,
        )
    ]

    result = check_required_information(
        condition=speed_condition,
        scene_elements=scene_elements,
    )

    assert result is not None
    assert result.condition_status == ConditionStatus.UNRESOLVED
    assert "Invalid / Unusable" in result.reason

def test_available_required_information_passes_information_gate():
    conditions = load_checking_conditions()

    heart_rate_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-01"
    )

    scene_elements = [
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
    ]

    result = check_required_information(
        condition=heart_rate_condition,
        scene_elements=scene_elements,
    )

    assert result is None

def test_unmappable_surface_makes_condition_unresolved():
    conditions = load_checking_conditions()

    surface_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-02"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-SURFACE_CONDITION-01",
            entity="Environment",
            attribute="surface_condition",
            value="Unsupported_surface_state",
            value_type="categorical",
            information_status=InformationStatus.AVAILABLE,
            temporal_characteristic="dynamic",
            cycle=1,
        )
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-SURFACE_CONDITION-01",
            mapping_status=MappingStatus.UNMAPPABLE,
            reason="No predefined mapping specification matched.",
        )
    ]

    result = check_required_mappings(
        condition=surface_condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assert result is not None
    assert result.condition_status == ConditionStatus.UNRESOLVED
    assert result.observed_value == "Unsupported_surface_state"
    assert "Unmappable" in result.reason

def test_missing_mapping_result_makes_condition_unresolved():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

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
        )
    ]

    result = check_required_mappings(
        condition=speed_condition,
        scene_elements=scene_elements,
        mapping_results=[],
    )

    assert result is not None
    assert result.condition_status == ConditionStatus.UNRESOLVED
    assert "no MappingResult" in result.reason

def test_mapped_required_attributes_pass_mapping_gate():
    conditions = load_checking_conditions()

    heart_rate_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-01"
    )

    scene_elements = [
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
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-HEART_RATE-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-06",
            ontology_reference="hasHeartFrequency",
        ),
        MappingResult(
            scene_element_id="SE-AGE-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-04",
            ontology_reference="Age_scalar",
        ),
    ]

    result = check_required_mappings(
        condition=heart_rate_condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assert result is None

def test_heart_rate_inside_range_is_satisfied():
    conditions = load_checking_conditions()

    heart_rate_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-01"
    )

    scene_elements = [
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
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-HEART_RATE-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-06",
            ontology_reference="hasHeartFrequency",
        ),
        MappingResult(
            scene_element_id="SE-AGE-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-04",
            ontology_reference="Age_scalar",
        ),
    ]

    result = evaluate_condition_operator(
        condition=heart_rate_condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assert result.condition_status == ConditionStatus.SATISFIED
    assert result.observed_value == 85
    assert result.ontology_reference == "hasHeartFrequency"

def test_heart_rate_outside_range_is_violated():
    conditions = load_checking_conditions()

    heart_rate_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-01"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-HEART_RATE-01",
            entity="Patient",
            attribute="heart_rate",
            value=110,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="bpm",
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
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-HEART_RATE-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-06",
            ontology_reference="hasHeartFrequency",
        ),
        MappingResult(
            scene_element_id="SE-AGE-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-04",
            ontology_reference="Age_scalar",
        ),
    ]

    result = evaluate_condition_operator(
        condition=heart_rate_condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assert result.condition_status == ConditionStatus.VIOLATED
    assert result.observed_value == 110

def test_vehicle_speed_at_limit_is_satisfied():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-VEHICLE_SPEED-01",
            entity="APTS_Vehicle",
            attribute="vehicle_speed",
            value=1.5,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="m/s",
            temporal_characteristic="dynamic",
            cycle=1,
        )
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-VEHICLE_SPEED-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-05",
            ontology_reference="speedValue",
        )
    ]

    result = evaluate_condition_operator(
        condition=speed_condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assert result.condition_status == ConditionStatus.SATISFIED

def test_vehicle_speed_above_limit_is_violated():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

    scene_elements = [
        SceneElement(
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
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-VEHICLE_SPEED-02",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-05",
            ontology_reference="speedValue",
        )
    ]

    result = evaluate_condition_operator(
        condition=speed_condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assert result.condition_status == ConditionStatus.VIOLATED
    assert result.observed_value == 1.6

def test_wet_surface_is_violated():
    conditions = load_checking_conditions()

    surface_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-02"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-SURFACE_CONDITION-01",
            entity="Environment",
            attribute="surface_condition",
            value="Wet",
            value_type="categorical",
            information_status=InformationStatus.AVAILABLE,
            temporal_characteristic="dynamic",
            cycle=1,
        )
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-SURFACE_CONDITION-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-03",
            ontology_reference="Wet",
        )
    ]

    result = evaluate_condition_operator(
        condition=surface_condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assert result.condition_status == ConditionStatus.VIOLATED
    assert result.observed_value == "Wet"
    assert result.ontology_reference == "Wet"

def test_check_condition_returns_none_when_not_applicable():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-TRANSPORT_TYPE-01",
            entity="Transport",
            attribute="transport_type",
            value="Other_transport",
            value_type="categorical",
            information_status=InformationStatus.AVAILABLE,
            temporal_characteristic="contextual",
            cycle=1,
        ),
        SceneElement(
            scene_element_id="SE-VEHICLE_SPEED-01",
            entity="APTS_Vehicle",
            attribute="vehicle_speed",
            value=1.6,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="m/s",
            temporal_characteristic="dynamic",
            cycle=1,
        ),
    ]

    result = check_condition(
        condition=speed_condition,
        scene_elements=scene_elements,
        mapping_results=[],
    )

    assert result is None

def test_check_condition_is_unresolved_when_applicability_is_unknown():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-TRANSPORT_TYPE-01",
            entity="Transport",
            attribute="transport_type",
            value=None,
            value_type="categorical",
            information_status=InformationStatus.MISSING,
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
    ]

    result = check_condition(
        condition=speed_condition,
        scene_elements=scene_elements,
        mapping_results=[],
    )

    assert result is not None
    assert result.condition_status == ConditionStatus.UNRESOLVED
    assert "SE-TRANSPORT_TYPE-01" in result.related_scene_element_ids
    assert "applicability" in result.reason

def test_check_condition_evaluates_speed_violation():
    conditions = load_checking_conditions()

    speed_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-03"
    )

    scene_elements = [
        SceneElement(
            scene_element_id="SE-TRANSPORT_TYPE-02",
            entity="Transport",
            attribute="transport_type",
            value="Patient_transport",
            value_type="categorical",
            information_status=InformationStatus.AVAILABLE,
            temporal_characteristic="contextual",
            cycle=2,
        ),
        SceneElement(
            scene_element_id="SE-VEHICLE_SPEED-02",
            entity="APTS_Vehicle",
            attribute="vehicle_speed",
            value=1.6,
            value_type="number",
            information_status=InformationStatus.AVAILABLE,
            unit="m/s",
            temporal_characteristic="dynamic",
            cycle=2,
        ),
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-VEHICLE_SPEED-02",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-05",
            ontology_reference="speedValue",
        )
    ]

    result = check_condition(
        condition=speed_condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assert result is not None
    assert result.condition_status == ConditionStatus.VIOLATED
    assert result.observed_value == 1.6
    assert result.ontology_reference == "speedValue"

def test_check_condition_skips_surface_condition_when_input_absent():
    conditions = load_checking_conditions()

    surface_condition = next(
        condition
        for condition in conditions
        if condition.condition_id == "A-02"
    )

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
        )
    ]

    result = check_condition(
        condition=surface_condition,
        scene_elements=scene_elements,
        mapping_results=[],
    )

    assert result is None

def test_evaluate_checking_conditions_for_normal_scene():
    conditions = load_checking_conditions()

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
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-HEART_RATE-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-06",
            ontology_reference="hasHeartFrequency",
        ),
        MappingResult(
            scene_element_id="SE-AGE-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-04",
            ontology_reference="Age_scalar",
        ),
        MappingResult(
            scene_element_id="SE-VEHICLE_SPEED-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-05",
            ontology_reference="speedValue",
        ),
    ]

    results = evaluate_checking_conditions(
        conditions=conditions,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assert len(results) == 2

    result_by_condition_id = {
        result.condition_id: result
        for result in results
    }

    assert (
        result_by_condition_id["A-01"].condition_status
        == ConditionStatus.SATISFIED
    )
    assert (
        result_by_condition_id["A-03"].condition_status
        == ConditionStatus.SATISFIED
    )

    assert "A-02" not in result_by_condition_id

def test_evaluate_checking_conditions_preserves_mixed_results():
    conditions = load_checking_conditions()

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
            scene_element_id="SE-HEART_RATE-01",
            entity="Patient",
            attribute="heart_rate",
            value=None,
            value_type="number",
            information_status=InformationStatus.MISSING,
            unit="bpm",
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
            scene_element_id="SE-SURFACE_CONDITION-01",
            entity="Environment",
            attribute="surface_condition",
            value="Wet",
            value_type="categorical",
            information_status=InformationStatus.AVAILABLE,
            temporal_characteristic="dynamic",
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
    ]

    mapping_results = [
        MappingResult(
            scene_element_id="SE-AGE-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-04",
            ontology_reference="Age_scalar",
        ),
        MappingResult(
            scene_element_id="SE-SURFACE_CONDITION-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-03",
            ontology_reference="Wet",
        ),
        MappingResult(
            scene_element_id="SE-VEHICLE_SPEED-01",
            mapping_status=MappingStatus.MAPPED,
            mapping_id="M-05",
            ontology_reference="speedValue",
        ),
    ]

    results = evaluate_checking_conditions(
        conditions=conditions,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    result_by_condition_id = {
        result.condition_id: result
        for result in results
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