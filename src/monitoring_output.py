"""Monitoring-output and human-response handling for the prototype.

This module applies a predefined response policy after the overall ODD
assessment has been determined. Response selection remains separate from
the assessment logic because human-response needs are case-dependent.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from src.models import (
    AssessmentState,
    ConditionResult,
    ConditionStatus,
    MonitoringResult,
    ResponseType,
)

DEFAULT_RESPONSE_RULES_PATH = Path(
    "data/config/response_rules.json"
)


@dataclass(frozen=True)
class ResponsePolicy:
    inside_odd: ResponseType
    unresolved: ResponseType
    violated_conditions: dict[str, ResponseType]
    priority: tuple[ResponseType, ...]


def load_response_policy(
    response_path: Path = DEFAULT_RESPONSE_RULES_PATH,
) -> ResponsePolicy:
    with response_path.open("r", encoding="utf-8") as file:
        raw_policy = json.load(file)

    violated_conditions = {
        condition_id: ResponseType(response_type)
        for condition_id, response_type
        in raw_policy["violated_conditions"].items()
    }

    priority = tuple(
        ResponseType(response_type)
        for response_type in raw_policy["priority"]
    )

    return ResponsePolicy(
        inside_odd=ResponseType(raw_policy["inside_odd"]),
        unresolved=ResponseType(raw_policy["unresolved"]),
        violated_conditions=violated_conditions,
        priority=priority,
    )

def _select_primary_response(
    candidates: list[ResponseType],
    policy: ResponsePolicy,
) -> ResponseType:
    for response_type in policy.priority:
        if response_type in candidates:
            return response_type

    raise ValueError(
        "No configured response priority matches the response candidates."
    )

def determine_response_type(
    assessment: AssessmentState,
    condition_results: list[ConditionResult],
    policy: ResponsePolicy,
) -> ResponseType:
    """Select the primary human-response category for one assessment.

    The response is case-dependent and is not derived from AssessmentState alone.
    When multiple response needs coexist, the configured priority selects one
    primary response while all ConditionResults remain preserved for traceability.
    """
    # Inside ODD normally requires no immediate human response in the
    # minimal prototype.
    if assessment == AssessmentState.INSIDE_ODD:
        return policy.inside_odd

    response_candidates = []

    # Violations use condition-specific response rules, while unresolved
    # information or mapping limitations request clarification.
    for result in condition_results:
        if result.condition_status == ConditionStatus.VIOLATED:
            try:
                response_type = policy.violated_conditions[
                    result.condition_id
                ]
            except KeyError as error:
                raise ValueError(
                    "No response rule is configured for violated "
                    f"condition '{result.condition_id}'."
                ) from error

            response_candidates.append(response_type)

        elif result.condition_status == ConditionStatus.UNRESOLVED:
            response_candidates.append(policy.unresolved)

    if not response_candidates:
        raise ValueError(
            f"Assessment '{assessment.value}' requires at least one "
            "response-relevant condition result."
        )

    # Priority affects only the single primary response stored in MonitoringResult;
    # it does not remove lower-priority needs from the underlying evidence.
    return _select_primary_response(
        candidates=response_candidates,
        policy=policy,
    )

def _build_monitoring_summary(
    assessment: AssessmentState,
    condition_results: list[ConditionResult],
) -> str:
    violated_ids = [
        result.condition_id
        for result in condition_results
        if result.condition_status == ConditionStatus.VIOLATED
    ]

    unresolved_details = [
        (
            f"{result.condition_id}: {result.reason}"
            if result.reason
            else result.condition_id
        )
        for result in condition_results
        if result.condition_status == ConditionStatus.UNRESOLVED
    ]

    if assessment == AssessmentState.INSIDE_ODD:
        return (
            "Inside ODD: all applicable checking conditions "
            "are satisfied."
        )

    if assessment == AssessmentState.OUTSIDE_ODD:
        summary = (
            "Outside ODD: violated condition(s): "
            + ", ".join(violated_ids)
            + "."
        )

        if unresolved_details:
            summary += (
                " Unresolved condition(s) retained for traceability: "
                + ", ".join(unresolved_details)
                + "."
            )

        return summary

    return (
        "Unclear: unresolved condition(s): "
        + ", ".join(unresolved_details)
        + "."
    )

def build_monitoring_result(
    scenario_id: str,
    cycle: int,
    assessment: AssessmentState,
    condition_results: list[ConditionResult],
    policy: ResponsePolicy,
) -> MonitoringResult:
    response = determine_response_type(
        assessment=assessment,
        condition_results=condition_results,
        policy=policy,
    )

    summary = _build_monitoring_summary(
        assessment=assessment,
        condition_results=condition_results,
    )

    return MonitoringResult(
        scenario_id=scenario_id,
        cycle=cycle,
        assessment=assessment,
        response=response,
        condition_results=condition_results,
        summary=summary,
    )