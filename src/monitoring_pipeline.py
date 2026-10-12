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
    """Process one runtime snapshot through the complete monitoring pipeline."""

    # Each call evaluates one independent runtime snapshot. The minimal prototype
    # does not perform temporal-history reasoning or prediction across cycles.
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

    return build_monitoring_result(
        scenario_id=scenario_id,
        cycle=cycle,
        assessment=assessment,
        condition_results=condition_results,
        policy=resources.response_policy,
    )