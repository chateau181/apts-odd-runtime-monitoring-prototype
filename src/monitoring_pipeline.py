"""End-to-end orchestration of one runtime monitoring cycle.

Static ontology and configuration resources are loaded once before runtime.
Each runtime snapshot is then processed through the complete monitoring
pipeline without modifying the ontology or configuration.
"""

from dataclasses import dataclass
from typing import Any

from rdflib import Graph

from src.assessment import determine_assessment_state
from src.checking import (
    evaluate_checking_conditions,
    load_checking_conditions,
)
from src.input_handler import normalize_runtime_snapshot
from src.models import (
    CheckingCondition,
    MappingSpecification,
    MonitoringCycleTrace,
    MonitoringResult,
)
from src.monitoring_output import (
    ResponsePolicy,
    build_monitoring_result,
    load_response_policy,
)
from src.ontology_access import load_ontology
from src.scene_representation import build_scene_representation
from src.semantic_mapping import (
    load_mapping_specifications,
    map_scene_representation,
)


@dataclass(frozen=True)
class MonitoringResources:
    ontology_graph: Graph
    mapping_specifications: list[MappingSpecification]
    checking_conditions: list[CheckingCondition]
    response_policy: ResponsePolicy

# Ontology and configuration are pre-runtime resources. They are loaded once
# and reused across snapshot-based monitoring cycles.
def load_monitoring_resources() -> MonitoringResources:
    """Load the fixed ontology and prototype configuration before runtime."""

    return MonitoringResources(
        ontology_graph=load_ontology(),
        mapping_specifications=load_mapping_specifications(),
        checking_conditions=load_checking_conditions(),
        response_policy=load_response_policy(),
    )

def run_monitoring_cycle(
    snapshot: dict[str, Any],
    scenario_id: str,
    cycle: int,
    resources: MonitoringResources,
) -> MonitoringResult:
    """Process one runtime snapshot and return its final monitoring result."""

    trace = run_monitoring_cycle_with_trace(
        snapshot=snapshot,
        scenario_id=scenario_id,
        cycle=cycle,
        resources=resources,
    )

    return trace.monitoring_result

def run_monitoring_cycle_with_trace(
    snapshot: dict[str, Any],
    scenario_id: str,
    cycle: int,
    resources: MonitoringResources,
) -> MonitoringCycleTrace:
    """Process one runtime snapshot and preserve the complete execution trace."""

    normalized_information = normalize_runtime_snapshot(
        snapshot=snapshot,
        cycle=cycle,
    )

    scene_elements = build_scene_representation(
        normalized_information=normalized_information,
    )

    mapping_results = map_scene_representation(
        scene_elements=scene_elements,
        specifications=resources.mapping_specifications,
        graph=resources.ontology_graph,
    )

    condition_results = evaluate_checking_conditions(
        conditions=resources.checking_conditions,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
    )

    assessment = determine_assessment_state(
        condition_results=condition_results,
    )

    monitoring_result = build_monitoring_result(
        scenario_id=scenario_id,
        cycle=cycle,
        assessment=assessment,
        condition_results=condition_results,
        policy=resources.response_policy,
    )

    return MonitoringCycleTrace(
        scenario_id=scenario_id,
        cycle=cycle,
        raw_snapshot=snapshot.copy(),
        normalized_information=normalized_information,
        scene_elements=scene_elements,
        mapping_results=mapping_results,
        condition_results=condition_results,
        monitoring_result=monitoring_result,
    )