from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class InformationStatus(str, Enum):
    AVAILABLE = "Available"
    MISSING = "Missing"
    INCONSISTENT = "Inconsistent"
    OUTDATED = "Outdated"
    INVALID_UNUSABLE = "Invalid / Unusable"


class MappingStatus(str, Enum):
    MAPPED = "Mapped"
    UNMAPPABLE = "Unmappable"


class MappingType(str, Enum):
    DIRECT = "Direct"
    STRUCTURED = "Structured / context-dependent"
    EXTENSION_SUPPORTED = "Extension-supported"


class ConditionOperator(str, Enum): # logic of Judgement
    RANGE_INCLUSIVE = "Range inclusive" # e.g.  60 <= Heart Rate <= 100
    LESS_EQUAL = "Less than or equal" # e.g. speed <= 1.5
    PROHIBITED_STATE = "Prohibited state" # e.g. wet is prohibited


class ConditionStatus(str, Enum):
    SATISFIED = "Satisfied"
    VIOLATED = "Violated"
    UNRESOLVED = "Unresolved"


class AssessmentState(str, Enum):
    INSIDE_ODD = "Inside ODD"
    OUTSIDE_ODD = "Outside ODD"
    UNCLEAR = "Unclear"


class ResponseType(str, Enum):
    NONE = "None"
    INTERVENTION = "Intervention"
    REVIEW = "Review"
    CLARIFICATION = "Clarification"


@dataclass
class NormalizedRuntimeInformation:
    attribute: str
    entity: str
    value: Any | None
    value_type: str

    unit: str | None = None
    source: str = "synthetic"
    temporal_characteristic: str | None = None
    cycle: int | None = None

    information_status: InformationStatus = InformationStatus.AVAILABLE


@dataclass
class SceneElement:
    scene_element_id: str

    entity: str
    attribute: str
    value: Any | None
    value_type: str

    information_status: InformationStatus

    unit: str | None = None
    source: str = "synthetic"
    temporal_characteristic: str | None = None
    cycle: int | None = None


@dataclass                   # In Semantic Mapping
class MappingSpecification:  # use pre-defined rules to check whether SceneElement can be mapped to Ontology
    mapping_id: str

    scene_attribute: str
    ontology_reference: str
    ontology_element_type: str
    mapping_type: MappingType

    scene_entity: str | None = None
    scene_value: Any | None = None

    supporting_ontology_references: dict[str, str] = field(
        default_factory=dict
    )


@dataclass
class MappingResult: # Pre-runtime specification used by Semantic Mapping.
    scene_element_id: str
    mapping_status: MappingStatus

    mapping_id: str | None = None
    ontology_reference: str | None = None
    ontology_element_type: str | None = None
    mapping_type: MappingType | None = None

    mapping_context: dict[str, Any] = field(default_factory=dict)
    reason: str | None = None


@dataclass
class CheckingCondition:  # Pre-runtime rule definition used by Checking.
    condition_id: str
    name: str
    checked_attribute: str
    required_attributes: tuple[str, ...]
    operator: ConditionOperator

    applicability_context: dict[str, Any] = field(default_factory=dict)
    activation_attribute: str | None = None

    unit: str | None = None
    minimum: float | None = None
    maximum: float | None = None
    prohibited_state: str | None = None

    provenance: str = ""
    assumption_status: str = ""

@dataclass
class ConditionResult: # Result of condition-checking
    condition_id: str
    condition_status: ConditionStatus
    checked_attribute: str
    observed_value: Any | None

    related_scene_element_ids: list[str] = field(default_factory=list)
    ontology_reference: str | None = None
    reason: str | None = None


@dataclass
class MonitoringResult:
    scenario_id: str
    cycle: int
    assessment: AssessmentState
    response: ResponseType

    condition_results: list[ConditionResult] = field(default_factory=list)
    summary: str | None = None