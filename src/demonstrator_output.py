"""Human-readable output formatting for the scenario demonstrator.

The formatter presents the already computed execution trace without changing
or re-evaluating any monitoring result.
"""

import json

from src.models import MonitoringCycleTrace, ScenarioExecutionResult

SEPARATOR = "=" * 72


def format_cycle_trace(trace: MonitoringCycleTrace) -> str:
    """Format one monitoring cycle as a readable execution trace."""

    lines = [
        SEPARATOR,
        f"Scenario: {trace.scenario_id} | Cycle: {trace.cycle}",
        SEPARATOR,
        "",
        "Runtime Input",
        json.dumps(
            trace.raw_snapshot,
            indent=2,
            ensure_ascii=False,
        ),
        "",
        "Scene Representation",
    ]

    for element in trace.scene_elements:
        value = (
            "<missing>"
            if element.value is None
            else str(element.value)
        )

        unit = f" {element.unit}" if element.unit else ""

        lines.append(
            f"  {element.scene_element_id}: "
            f"{element.entity}.{element.attribute} = "
            f"{value}{unit} "
            f"[{element.information_status.value}]"
        )

    lines.extend(
        [
            "",
            "Semantic Mapping",
        ]
    )

    for mapping in trace.mapping_results:
        ontology_reference = mapping.ontology_reference or "-"

        lines.append(
            f"  {mapping.scene_element_id}: "
            f"{mapping.mapping_status.value} "
            f"-> {ontology_reference}"
        )

    lines.extend(
        [
            "",
            "Checking Results",
        ]
    )

    for result in trace.condition_results:
        observed_value = (
            "<missing>"
            if result.observed_value is None
            else str(result.observed_value)
        )

        result_line = (
            f"  {result.condition_id}: "
            f"{result.condition_status.value} "
            f"| observed={observed_value}"
        )

        if result.reason:
            result_line += f" | reason={result.reason}"

        lines.append(result_line)

    monitoring_result = trace.monitoring_result

    lines.extend(
        [
            "",
            "Monitoring Result",
            f"  Assessment: {monitoring_result.assessment.value}",
            f"  Primary Response: {monitoring_result.response.value}",
            f"  Summary: {monitoring_result.summary or '-'}",
        ]
    )

    return "\n".join(lines)

def format_scenario_summary(
    execution: ScenarioExecutionResult,
) -> str:
    """Format a compact overview of all monitoring cycles."""

    condition_ids = sorted(
        {
            result.condition_id
            for trace in execution.cycle_traces
            for result in trace.condition_results
        }
    )

    header_columns = [
        "Cycle",
        *condition_ids,
        "Assessment",
        "Response",
    ]

    rows = [
        " | ".join(header_columns)
    ]

    rows.append("-" * len(rows[0]))

    for trace in execution.cycle_traces:
        condition_statuses = {
            result.condition_id: result.condition_status.value
            for result in trace.condition_results
        }

        monitoring_result = trace.monitoring_result

        row = [
            str(trace.cycle),
            *[
                condition_statuses.get(
                    condition_id,
                    "N/A",
                )
                for condition_id in condition_ids
            ],
            monitoring_result.assessment.value,
            monitoring_result.response.value,
        ]

        rows.append(" | ".join(row))

    return "\n".join(
        [
            "Scenario Summary",
            "",
            *rows,
        ]
    )

def format_scenario_execution(
    execution: ScenarioExecutionResult,
) -> str:
    """Format the complete execution of one runtime scenario."""

    header = "\n".join(
        [
            SEPARATOR,
            f"Scenario Execution: {execution.scenario_id}",
            f"Description: {execution.description}",
            f"Cycles: {len(execution.cycle_traces)}",
            SEPARATOR,
        ]
    )

    formatted_cycles = [
        format_cycle_trace(trace)
        for trace in execution.cycle_traces
    ]

    summary = format_scenario_summary(
        execution=execution,
    )

    return (
            header
            + "\n\n"
            + summary
            + "\n\n"
            + "\n\n".join(formatted_cycles)
    )