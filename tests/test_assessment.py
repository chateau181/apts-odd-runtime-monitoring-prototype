import pytest

from src.assessment import determine_assessment_state
from src.models import (
    AssessmentState,
    ConditionResult,
    ConditionStatus,
)


def test_all_satisfied_conditions_produce_inside_odd():
    condition_results = [
        ConditionResult(
            condition_id="A-01",
            condition_status=ConditionStatus.SATISFIED,
            checked_attribute="heart_rate",
            observed_value=85,
        ),
        ConditionResult(
            condition_id="A-03",
            condition_status=ConditionStatus.SATISFIED,
            checked_attribute="vehicle_speed",
            observed_value=1.2,
        ),
    ]

    assessment = determine_assessment_state(condition_results)

    assert assessment == AssessmentState.INSIDE_ODD

def test_violated_condition_produces_outside_odd():
    condition_results = [
        ConditionResult(
            condition_id="A-01",
            condition_status=ConditionStatus.SATISFIED,
            checked_attribute="heart_rate",
            observed_value=85,
        ),
        ConditionResult(
            condition_id="A-03",
            condition_status=ConditionStatus.VIOLATED,
            checked_attribute="vehicle_speed",
            observed_value=1.6,
        ),
    ]

    assessment = determine_assessment_state(condition_results)

    assert assessment == AssessmentState.OUTSIDE_ODD

def test_unresolved_condition_without_violation_produces_unclear():
    condition_results = [
        ConditionResult(
            condition_id="A-01",
            condition_status=ConditionStatus.UNRESOLVED,
            checked_attribute="heart_rate",
            observed_value=None,
            reason="Required heart-rate information is missing.",
        ),
        ConditionResult(
            condition_id="A-03",
            condition_status=ConditionStatus.SATISFIED,
            checked_attribute="vehicle_speed",
            observed_value=1.2,
        ),
    ]

    assessment = determine_assessment_state(condition_results)

    assert assessment == AssessmentState.UNCLEAR

def test_violation_takes_precedence_over_unresolved_condition():
    condition_results = [
        ConditionResult(
            condition_id="A-01",
            condition_status=ConditionStatus.UNRESOLVED,
            checked_attribute="heart_rate",
            observed_value=None,
        ),
        ConditionResult(
            condition_id="A-02",
            condition_status=ConditionStatus.VIOLATED,
            checked_attribute="surface_condition",
            observed_value="Wet",
        ),
        ConditionResult(
            condition_id="A-03",
            condition_status=ConditionStatus.SATISFIED,
            checked_attribute="vehicle_speed",
            observed_value=1.2,
        ),
    ]

    assessment = determine_assessment_state(condition_results)

    assert assessment == AssessmentState.OUTSIDE_ODD

def test_empty_condition_results_cannot_be_assessed():
    with pytest.raises(ValueError):
        determine_assessment_state([])