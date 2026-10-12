"""Condition-level evaluation for the runtime ODD monitoring prototype.

This module applies predefined CheckingConditions to one Scene Representation.
It first determines whether a condition is applicable, then verifies required
runtime information and semantic mappings, and finally evaluates the configured
operator.

The output of this module is limited to Satisfied, Violated, and Unresolved
ConditionResults. Overall Inside ODD / Outside ODD / Unclear assessment is
performed by a later assessment layer.
"""
import json
from pathlib import Path

from src.models import (
    CheckingCondition,
    ConditionOperator,
    ConditionResult,
    ConditionStatus,
    InformationStatus,
    MappingResult,
    MappingStatus,
    SceneElement,
)

DEFAULT_CHECKING_CONDITIONS_PATH = Path(
    "data/config/checking_conditions.json"
)


def load_checking_conditions(
    conditions_path: Path = DEFAULT_CHECKING_CONDITIONS_PATH,
) -> list[CheckingCondition]:
    """Load pre-runtime checking-condition definitions from JSON."""
    with conditions_path.open("r", encoding="utf-8") as file:
        raw_conditions = json.load(file)

    conditions = []

    for definition in raw_conditions:
        condition = CheckingCondition(
            condition_id=definition["condition_id"],
            name=definition["name"],
            checked_attribute=definition["checked_attribute"],
            required_attributes=tuple(definition["required_attributes"]),
            operator=ConditionOperator(definition["operator"]),
            applicability_context=definition.get(
                "applicability_context",
                {},
            ),
            activation_attribute=definition.get("activation_attribute"),
            unit=definition.get("unit"),
            minimum=definition.get("minimum"),
            maximum=definition.get("maximum"),
            prohibited_state=definition.get("prohibited_state"),
            provenance=definition.get("provenance", ""),
            assumption_status=definition.get(
                "assumption_status",
                "",
            ),
        )

        conditions.append(condition)

    return conditions

def _find_scene_element(
    scene_elements: list[SceneElement],
    attribute: str,
) -> SceneElement | None:
    """Find the Scene Element representing one runtime attribute."""
    return next(
        (
            element
            for element in scene_elements
            if element.attribute == attribute
        ),
        None,
    )

def _find_mapping_result(
    mapping_results: list[MappingResult],
    scene_element_id: str,
) -> MappingResult | None:
    return next(
        (
            result
            for result in mapping_results
            if result.scene_element_id == scene_element_id
        ),
        None,
    )

"""Determine whether a condition applies to the current scene.

Returns:
    True: the condition is applicable.
    False: the condition is definitely not applicable.
    None: applicability cannot be determined from the available context.
"""
def determine_condition_applicability(
    condition: CheckingCondition,
    scene_elements: list[SceneElement],
) -> bool | None:
    # An activation attribute distinguishes an optional condition that is absent
    # from a condition whose input is present but currently unusable or missing.
    if condition.activation_attribute is not None:
        activation_element = _find_scene_element(
            scene_elements=scene_elements,
            attribute=condition.activation_attribute,
        )

        if activation_element is None:
            return False

    for attribute, expected_value in condition.applicability_context.items():
        context_element = _find_scene_element(
            scene_elements=scene_elements,
            attribute=attribute,
        )

        if context_element is None:
            return None

        if context_element.information_status != InformationStatus.AVAILABLE:
            return None

        if context_element.value != expected_value:
            return False

    return True


"""Return Unresolved when required runtime information is unavailable.

A return value of None means that the information-quality gate passed and
checking may continue to semantic-mapping validation.
"""
def check_required_information(
    condition: CheckingCondition,
    scene_elements: list[SceneElement],
) -> ConditionResult | None:
    related_scene_element_ids = []
    issues = []

    checked_element = _find_scene_element(
        scene_elements=scene_elements,
        attribute=condition.checked_attribute,
    )

    observed_value = (
        checked_element.value
        if checked_element is not None
        else None
    )

    for attribute in condition.required_attributes:
        scene_element = _find_scene_element(
            scene_elements=scene_elements,
            attribute=attribute,
        )

        if scene_element is None:
            issues.append(
                f"Required attribute '{attribute}' is absent "
                "from the Scene Representation."
            )
            continue

        related_scene_element_ids.append(
            scene_element.scene_element_id
        )

        # Missing or unusable information cannot prove either satisfaction or
        # violation, so the condition remains Unresolved.
        if scene_element.information_status != InformationStatus.AVAILABLE:
            issues.append(
                f"Required attribute '{attribute}' has information "
                f"status '{scene_element.information_status.value}'."
            )

    if not issues:
        return None

    return ConditionResult(
        condition_id=condition.condition_id,
        condition_status=ConditionStatus.UNRESOLVED,
        checked_attribute=condition.checked_attribute,
        observed_value=observed_value,
        related_scene_element_ids=related_scene_element_ids,
        reason=" ".join(issues),
    )

"""Verify semantic mappings required for evaluating a condition.

A return value of None means that all required mappings are sufficient.
Missing or Unmappable semantic correspondences produce Unresolved.
"""
# Checking does not bypass the Semantic Mapping layer. Even an Available
# runtime value must have sufficient semantic correspondence before evaluation.
def check_required_mappings(
    condition: CheckingCondition,
    scene_elements: list[SceneElement],
    mapping_results: list[MappingResult],
) -> ConditionResult | None:
    related_scene_element_ids = []
    issues = []

    checked_element = _find_scene_element(
        scene_elements=scene_elements,
        attribute=condition.checked_attribute,
    )

    observed_value = (
        checked_element.value
        if checked_element is not None
        else None
    )

    checked_mapping = None

    if checked_element is not None:
        checked_mapping = _find_mapping_result(
            mapping_results=mapping_results,
            scene_element_id=checked_element.scene_element_id,
        )

    for attribute in condition.required_attributes:
        scene_element = _find_scene_element(
            scene_elements=scene_elements,
            attribute=attribute,
        )

        if scene_element is None:
            issues.append(
                f"Required attribute '{attribute}' has no Scene Element "
                "for semantic mapping."
            )
            continue

        related_scene_element_ids.append(
            scene_element.scene_element_id
        )

        mapping_result = _find_mapping_result(
            mapping_results=mapping_results,
            scene_element_id=scene_element.scene_element_id,
        )

        if mapping_result is None:
            issues.append(
                f"Required attribute '{attribute}' has no MappingResult."
            )
            continue

        if mapping_result.mapping_status != MappingStatus.MAPPED:
            issues.append(
                f"Required attribute '{attribute}' has mapping status "
                f"'{mapping_result.mapping_status.value}'."
            )

    if not issues:
        return None

    ontology_reference = None

    if (
        checked_mapping is not None
        and checked_mapping.mapping_status == MappingStatus.MAPPED
    ):
        ontology_reference = checked_mapping.ontology_reference

    return ConditionResult(
        condition_id=condition.condition_id,
        condition_status=ConditionStatus.UNRESOLVED,
        checked_attribute=condition.checked_attribute,
        observed_value=observed_value,
        related_scene_element_ids=related_scene_element_ids,
        ontology_reference=ontology_reference,
        reason=" ".join(issues),
    )

"""Evaluate the configured operator after all prerequisite gates passed."""
# This function assumes applicability, information quality, and semantic
# mapping have already been validated by check_condition().
def evaluate_condition_operator(
    condition: CheckingCondition,
    scene_elements: list[SceneElement],
    mapping_results: list[MappingResult],
) -> ConditionResult:
    checked_element = _find_scene_element(
        scene_elements=scene_elements,
        attribute=condition.checked_attribute,
    )

    if checked_element is None:
        raise ValueError(
            f"Checked attribute '{condition.checked_attribute}' "
            "is missing from the Scene Representation."
        )

    checked_mapping = _find_mapping_result(
        mapping_results=mapping_results,
        scene_element_id=checked_element.scene_element_id,
    )

    related_scene_element_ids = []

    for attribute in condition.required_attributes:
        scene_element = _find_scene_element(
            scene_elements=scene_elements,
            attribute=attribute,
        )

        if scene_element is not None:
            related_scene_element_ids.append(
                scene_element.scene_element_id
            )

    # Inclusive range: both configured boundaries are accepted.
    if condition.operator == ConditionOperator.RANGE_INCLUSIVE:
        condition_satisfied = (
            condition.minimum
            <= checked_element.value
            <= condition.maximum
        )

    # A prohibited state violates the condition when it is observed.
    elif condition.operator == ConditionOperator.LESS_EQUAL:
        condition_satisfied = (
            checked_element.value <= condition.maximum
        )

    elif condition.operator == ConditionOperator.PROHIBITED_STATE:
        condition_satisfied = (
            checked_element.value != condition.prohibited_state
        )

    else:
        raise ValueError(
            f"Unsupported condition operator: {condition.operator}"
        )

    condition_status = (
        ConditionStatus.SATISFIED
        if condition_satisfied
        else ConditionStatus.VIOLATED
    )

    ontology_reference = (
        checked_mapping.ontology_reference
        if checked_mapping is not None
        else None
    )

    return ConditionResult(
        condition_id=condition.condition_id,
        condition_status=condition_status,
        checked_attribute=condition.checked_attribute,
        observed_value=checked_element.value,
        related_scene_element_ids=related_scene_element_ids,
        ontology_reference=ontology_reference,
    )

"""Evaluate one CheckingCondition using the defined decision sequence.

Decision order:
1. Determine applicability.
2. Verify required runtime information.
3. Verify required semantic mappings.
4. Evaluate the configured operator.

None is returned only when the condition is definitely not applicable.
"""
def check_condition(
    condition: CheckingCondition,
    scene_elements: list[SceneElement],
    mapping_results: list[MappingResult],
) -> ConditionResult | None:
    # False means definitely not applicable and therefore produces no
    # ConditionResult. None means applicability itself is uncertain and must be
    # preserved as Unresolved.
    applicability = determine_condition_applicability(
        condition=condition,
        scene_elements=scene_elements,
    )

    if applicability is False:
        return None

    if applicability is None:
        checked_element = _find_scene_element(
            scene_elements=scene_elements,
            attribute=condition.checked_attribute,
        )

        observed_value = (
            checked_element.value
            if checked_element is not None
            else None
        )

        related_scene_element_ids = []

        if checked_element is not None:
            related_scene_element_ids.append(
                checked_element.scene_element_id
            )

        for context_attribute in condition.applicability_context:
            context_element = _find_scene_element(
                scene_elements=scene_elements,
                attribute=context_attribute,
            )

            if (
                    context_element is not None
                    and context_element.scene_element_id
                    not in related_scene_element_ids
            ):
                related_scene_element_ids.append(
                    context_element.scene_element_id
                )

        return ConditionResult(
            condition_id=condition.condition_id,
            condition_status=ConditionStatus.UNRESOLVED,
            checked_attribute=condition.checked_attribute,
            observed_value=observed_value,
            related_scene_element_ids=related_scene_element_ids,
            reason=(
                "Condition applicability cannot be determined "
                "from the available scene context."
            ),
        )

    # Information-quality problems take precedence over mapping problems because
    # unavailable information is not sent through Semantic Mapping.
    information_result = check_required_information(
        condition=condition,
        scene_elements=scene_elements,
    )

    if information_result is not None:
        return information_result

    mapping_result = check_required_mappings(
        condition=condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    if mapping_result is not None:
        return mapping_result

    return evaluate_condition_operator(
        condition=condition,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

"""Evaluate all configured conditions for one runtime scene snapshot."""
def evaluate_checking_conditions(
    conditions: list[CheckingCondition],
    scene_elements: list[SceneElement],
    mapping_results: list[MappingResult],
) -> list[ConditionResult]:
    condition_results = []

    for condition in conditions:
        result = check_condition(
            condition=condition,
            scene_elements=scene_elements,
            mapping_results=mapping_results,
        )

        # Not-applicable conditions produce no ConditionResult and are therefore
        # excluded from the condition-level result set.
        if result is not None:
            condition_results.append(result)

    return condition_results