from src.models import (
    AssessmentState,
    ConditionResult,
    ConditionStatus,
    ResponseType,
)
from src.monitoring_output import (
    build_monitoring_result,
    determine_response_type,
    load_response_policy,
)


def test_load_response_policy():
    policy = load_response_policy()

    assert policy.inside_odd == ResponseType.NONE
    assert policy.unresolved == ResponseType.CLARIFICATION

    assert (
        policy.violated_conditions["A-01"]
        == ResponseType.REVIEW
    )

    assert (
        policy.violated_conditions["A-02"]
        == ResponseType.INTERVENTION
    )

    assert (
        policy.violated_conditions["A-03"]
        == ResponseType.INTERVENTION
    )


def test_response_priority_is_loaded_in_order():
    policy = load_response_policy()

    assert policy.priority == (
        ResponseType.INTERVENTION,
        ResponseType.REVIEW,
        ResponseType.CLARIFICATION,
        ResponseType.NONE,
    )

def test_inside_odd_requires_no_response():
    policy = load_response_policy()

    condition_results = [
        ConditionResult(
            condition_id="A-01",
            condition_status=ConditionStatus.SATISFIED,
            checked_attribute="heart_rate",
            observed_value=85,
        )
    ]

    response = determine_response_type(
        assessment=AssessmentState.INSIDE_ODD,
        condition_results=condition_results,
        policy=policy,
    )

    assert response == ResponseType.NONE

def test_heart_rate_violation_requires_review():
    policy = load_response_policy()

    condition_results = [
        ConditionResult(
            condition_id="A-01",
            condition_status=ConditionStatus.VIOLATED,
            checked_attribute="heart_rate",
            observed_value=110,
        )
    ]

    response = determine_response_type(
        assessment=AssessmentState.OUTSIDE_ODD,
        condition_results=condition_results,
        policy=policy,
    )

    assert response == ResponseType.REVIEW

def test_speed_violation_requires_intervention():
    policy = load_response_policy()

    condition_results = [
        ConditionResult(
            condition_id="A-03",
            condition_status=ConditionStatus.VIOLATED,
            checked_attribute="vehicle_speed",
            observed_value=1.6,
        )
    ]

    response = determine_response_type(
        assessment=AssessmentState.OUTSIDE_ODD,
        condition_results=condition_results,
        policy=policy,
    )

    assert response == ResponseType.INTERVENTION

def test_unresolved_condition_requires_clarification():
    policy = load_response_policy()

    condition_results = [
        ConditionResult(
            condition_id="A-01",
            condition_status=ConditionStatus.UNRESOLVED,
            checked_attribute="heart_rate",
            observed_value=None,
            reason="Required heart-rate information is missing.",
        )
    ]

    response = determine_response_type(
        assessment=AssessmentState.UNCLEAR,
        condition_results=condition_results,
        policy=policy,
    )

    assert response == ResponseType.CLARIFICATION

def test_intervention_has_priority_over_clarification():
    policy = load_response_policy()

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
    ]

    response = determine_response_type(
        assessment=AssessmentState.OUTSIDE_ODD,
        condition_results=condition_results,
        policy=policy,
    )

    assert response == ResponseType.INTERVENTION

def test_intervention_has_priority_over_review():
    policy = load_response_policy()

    condition_results = [
        ConditionResult(
            condition_id="A-01",
            condition_status=ConditionStatus.VIOLATED,
            checked_attribute="heart_rate",
            observed_value=110,
        ),
        ConditionResult(
            condition_id="A-03",
            condition_status=ConditionStatus.VIOLATED,
            checked_attribute="vehicle_speed",
            observed_value=1.6,
        ),
    ]

    response = determine_response_type(
        assessment=AssessmentState.OUTSIDE_ODD,
        condition_results=condition_results,
        policy=policy,
    )

    assert response == ResponseType.INTERVENTION

def test_build_inside_monitoring_result():
    policy = load_response_policy()

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

    result = build_monitoring_result(
        scenario_id="DS-01",
        cycle=1,
        assessment=AssessmentState.INSIDE_ODD,
        condition_results=condition_results,
        policy=policy,
    )

    assert result.scenario_id == "DS-01"
    assert result.cycle == 1
    assert result.assessment == AssessmentState.INSIDE_ODD
    assert result.response == ResponseType.NONE
    assert result.condition_results == condition_results
    assert "Inside ODD" in result.summary

def test_build_outside_monitoring_result_for_speed_violation():
    policy = load_response_policy()

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

    result = build_monitoring_result(
        scenario_id="DS-01",
        cycle=2,
        assessment=AssessmentState.OUTSIDE_ODD,
        condition_results=condition_results,
        policy=policy,
    )

    assert result.assessment == AssessmentState.OUTSIDE_ODD
    assert result.response == ResponseType.INTERVENTION
    assert "A-03" in result.summary

def test_build_unclear_monitoring_result():
    policy = load_response_policy()

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

    result = build_monitoring_result(
        scenario_id="DS-01",
        cycle=3,
        assessment=AssessmentState.UNCLEAR,
        condition_results=condition_results,
        policy=policy,
    )

    assert result.assessment == AssessmentState.UNCLEAR
    assert result.response == ResponseType.CLARIFICATION
    assert "missing" in result.summary.lower()
    assert "A-01" in result.summary

def test_mixed_monitoring_result_preserves_unresolved_evidence():
    policy = load_response_policy()

    condition_results = [
        ConditionResult(
            condition_id="A-01",
            condition_status=ConditionStatus.UNRESOLVED,
            checked_attribute="heart_rate",
            observed_value=None,
            reason="Required heart-rate information is missing.",
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

    result = build_monitoring_result(
        scenario_id="EC-Mixed",
        cycle=1,
        assessment=AssessmentState.OUTSIDE_ODD,
        condition_results=condition_results,
        policy=policy,
    )

    assert result.assessment == AssessmentState.OUTSIDE_ODD
    assert result.response == ResponseType.INTERVENTION

    assert len(result.condition_results) == 3

    assert any(
        condition.condition_status == ConditionStatus.UNRESOLVED
        for condition in result.condition_results
    )

    assert "A-02" in result.summary
    assert "A-01" in result.summary