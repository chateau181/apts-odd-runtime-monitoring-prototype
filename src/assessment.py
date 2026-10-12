"""Overall ODD assessment from condition-level checking results.

This module aggregates applicable ConditionResults into one overall assessment
for the configured checking context.

The aggregation follows the Conception decision semantics:
- any Violated condition -> Outside ODD
- otherwise any Unresolved condition -> Unclear
- otherwise all applicable conditions Satisfied -> Inside ODD
"""

from src.models import (
    AssessmentState,
    ConditionResult,
    ConditionStatus,
)


def determine_assessment_state(
    condition_results: list[ConditionResult],
) -> AssessmentState:
    if not condition_results:
        raise ValueError(
            "Overall assessment requires at least one applicable "
            "ConditionResult."
        )

    # Violated has precedence over Unresolved. A confirmed violation therefore
    # produces Outside ODD even when uncertainty exists in another condition.
    if any(
        result.condition_status == ConditionStatus.VIOLATED
        for result in condition_results
    ):
        return AssessmentState.OUTSIDE_ODD

    # Unresolved leads to Unclear only when no confirmed violation exists.
    if any(
        result.condition_status == ConditionStatus.UNRESOLVED
        for result in condition_results
    ):
        return AssessmentState.UNCLEAR

    return AssessmentState.INSIDE_ODD