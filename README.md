# APTS ODD Runtime Monitoring Prototype

A minimal Python demonstrator for ontology-supported runtime monitoring of selected Operational Design Domain (ODD) conditions for an Automated Patient Transport System (APTS).

The prototype demonstrates how heterogeneous runtime information can be transformed into a structured scene representation, semantically related to an existing ontology-based ODD model, evaluated using predefined Checking Conditions, and aggregated into a traceable overall monitoring result.

This repository was developed as part of a Forschungsarbeit at the University of Stuttgart.

---

## Overview

The prototype implements the following runtime monitoring pipeline:

```text
Runtime Snapshot
        ↓
Input Handling
        ↓
Normalized Runtime Information
        ↓
Scene Representation
        ↓
Semantic Mapping
        ↓
Condition-Level Checking
        ↓
Overall Assessment
        ↓
Monitoring Output
```

The processing chain distinguishes five different status layers:

```text
Information Status
Available / Missing / Inconsistent / Outdated / Invalid-Unusable

        ↓

Mapping Status
Mapped / Unmappable

        ↓

Condition Status
Satisfied / Violated / Unresolved

        ↓

Assessment State
Inside ODD / Outside ODD / Unclear

        ↓

Response Type
None / Intervention / Review / Clarification
```

A central design principle is that uncertainty is preserved explicitly.

For example:

```text
Missing runtime information
→ Unresolved condition
→ potentially Unclear assessment
```

and:

```text
Available runtime information
→ Unmappable
→ Unresolved condition
→ potentially Unclear assessment
```

Missing or semantically unmappable information is therefore not automatically interpreted as an ODD violation.

---

## Main Features

- Python-based end-to-end monitoring demonstrator
- Snapshot-based runtime processing
- External JSON scenario input
- Read-only access to an existing RDF/OWL ontology
- Deterministic predefined semantic mappings
- External mapping, checking, and response configuration
- Explicit distinction between information quality and semantic mappability
- Condition-level `Satisfied / Violated / Unresolved` semantics
- Overall `Inside ODD / Outside ODD / Unclear` assessment
- Case-dependent monitoring response
- Complete execution trace for demonstrator and evaluation purposes
- Unit, integration, end-to-end, scenario, output, and CLI tests
- Command-line interface for running predefined scenarios

---

## Project Structure

```text
apts_odd_prototype/
├── data/
│   ├── config/
│   │   ├── mapping_definitions.json
│   │   ├── checking_conditions.json
│   │   └── response_rules.json
│   │
│   ├── ontology/
│   │   └── final_ontology.rdf
│   │
│   └── scenarios/
│       ├── ds_01_dynamic.json
│       ├── ec_unmappable.json
│       └── ec_mixed.json
│
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── input_handler.py
│   ├── scene_representation.py
│   ├── ontology_access.py
│   ├── semantic_mapping.py
│   ├── checking.py
│   ├── assessment.py
│   ├── monitoring_output.py
│   ├── monitoring_pipeline.py
│   ├── scenario_loader.py
│   ├── scenario_runner.py
│   ├── demonstrator_output.py
│   └── run_demonstrator.py
│
├── tests/
├── prototype_decision_log.md
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

### Main Responsibilities

| Component | Responsibility |
|---|---|
| `input_handler.py` | Normalize raw runtime input and determine Information Status |
| `scene_representation.py` | Build structured runtime Scene Elements |
| `ontology_access.py` | Provide read-only ontology access |
| `semantic_mapping.py` | Relate Scene Elements to predefined ontology references |
| `checking.py` | Evaluate applicability, information, mapping, and operators |
| `assessment.py` | Aggregate Condition Results into Inside / Outside / Unclear |
| `monitoring_output.py` | Select the response and construct the Monitoring Result |
| `monitoring_pipeline.py` | Orchestrate one complete monitoring cycle |
| `scenario_loader.py` | Load external JSON scenarios |
| `scenario_runner.py` | Execute scenario cycles using the monitoring core |
| `demonstrator_output.py` | Generate human-readable summaries and traces |
| `run_demonstrator.py` | Provide the command-line entry point |

---

## Requirements

The prototype was developed with:

- Python 3.10
- RDFLib
- pytest
- Ruff

The required package versions are defined in:

```text
requirements.txt
requirements-dev.txt
```

---

## Quick Start

Clone the repository:

```bash
git clone https://github.com/chateau181/apts-odd-runtime-monitoring-prototype.git
cd apts-odd-runtime-monitoring-prototype
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

or on Linux/macOS:

```bash
source .venv/bin/activate
```

Install the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

---

## Running the Demonstrator

Run the default dynamic scenario:

```bash
python -m src.run_demonstrator
```

This executes `DS-01`.

You can also select a scenario explicitly.

### Dynamic Scenario

```bash
python -m src.run_demonstrator --scenario ds-01
```

### Unmappable Edge Case

```bash
python -m src.run_demonstrator --scenario ec-unmappable
```

### Mixed Edge Case

```bash
python -m src.run_demonstrator --scenario ec-mixed
```

Display the available CLI options:

```bash
python -m src.run_demonstrator --help
```

---

## Implemented Scenarios

### DS-01 — Dynamic Patient Transport Scenario

The main demonstrator consists of five sequentially executed runtime snapshots.

| Cycle | Runtime Situation | Assessment | Primary Response |
|---|---|---|---|
| t1 | Nominal state | Inside ODD | None |
| t2 | Vehicle speed = 1.6 m/s | Outside ODD | Intervention |
| t3 | Heart rate missing | Unclear | Clarification |
| t4 | Wet surface | Outside ODD | Intervention |
| t5 | Nominal state | Inside ODD | None |

The cycles are executed sequentially for demonstration purposes, but every cycle is evaluated independently.

The prototype does not perform temporal-history reasoning or prediction across cycles.

---

### EC-Unmappable

This scenario demonstrates the distinction between runtime information quality and semantic mappability.

```text
surface_condition = Unsupported_surface_state
        ↓
Information Status = Available
        ↓
Mapping Status = Unmappable
        ↓
A-02 = Unresolved
        ↓
Assessment = Unclear
        ↓
Response = Clarification
```

---

### EC-Mixed

This scenario demonstrates the coexistence of a confirmed violation and unresolved information.

```text
heart_rate = Missing
→ A-01 = Unresolved

surface_condition = Wet
→ A-02 = Violated

vehicle_speed = 1.2 m/s
→ A-03 = Satisfied
```

The overall result is:

```text
Assessment = Outside ODD
Primary Response = Intervention
```

The unresolved heart-rate evidence remains preserved in the Condition Results.

---

## Checking Conditions

The minimal prototype contains three representative Checking Conditions.

| ID | Checking Condition | Prototype Rule |
|---|---|---|
| A-01 | Adult resting heart-rate range | 60 ≤ HR ≤ 100 bpm |
| A-02 | Surface condition | `Wet` is treated as a prohibited state |
| A-03 | APTS vehicle speed | speed ≤ 1.5 m/s |

The use of these conditions and thresholds in the demonstrator is specific to the research prototype.

They must not be interpreted as validated hospital operational, clinical, or safety procedures.

---

## Semantic Mapping

Semantic mappings are defined externally in:

```text
data/config/mapping_definitions.json
```

Representative mappings include:

```text
Wet
→ Wet

vehicle_speed
→ speedValue

heart_rate
→ hasHeartFrequency
```

Semantic mapping is deterministic and predefined before runtime.

The prototype does not use:

- LLM-based mapping;
- similarity-based ontology matching;
- runtime ontology modification.

Runtime values remain in the runtime Scene Representation and mapping context.

The ontology is used as a read-only semantic reference.

---

## Checking Logic

An applicable Checking Condition is evaluated through several gates:

```text
Applicability
      ↓
Required Information
      ↓
Required Semantic Mapping
      ↓
Operator Evaluation
      ↓
Satisfied / Violated / Unresolved
```

Only when the required runtime information and semantic mapping are sufficient can the configured operator produce a definitive `Satisfied` or `Violated` result.

Otherwise, uncertainty is preserved as `Unresolved`.

---

## Overall Assessment

Condition-level results are aggregated deterministically:

```text
All applicable conditions Satisfied
→ Inside ODD

Any condition Violated
→ Outside ODD

No Violated condition
+ at least one Unresolved condition
→ Unclear
```

A confirmed violation has precedence over an unresolved condition when determining the overall assessment.

However, unresolved evidence remains available for traceability.

---

## Monitoring Response

The prototype uses the following predefined response policy:

```text
Inside ODD
→ None

A-01 violation
→ Review

A-02 violation
→ Intervention

A-03 violation
→ Intervention

Unresolved condition
→ Clarification
```

When several response needs coexist, the demonstrator selects one primary response using the priority:

```text
Intervention
>
Review
>
Clarification
>
None
```

This priority affects only the primary response stored in the final Monitoring Result.

Underlying Condition Results and unresolved reasons remain preserved.

The response assignments are prototype-specific design decisions and do not represent validated hospital procedures.

---

## Execution Trace

For research evaluation and demonstration, the prototype can preserve a complete execution trace for every monitoring cycle:

```text
Raw Runtime Snapshot
        ↓
Normalized Runtime Information
        ↓
Scene Elements
        ↓
Mapping Results
        ↓
Condition Results
        ↓
Monitoring Result
```

The demonstrator uses:

```python
run_monitoring_cycle_with_trace()
```

when intermediate processing evidence is required.

For consumers that only require the final monitoring result, the core also provides:

```python
run_monitoring_cycle()
```

which returns the final `MonitoringResult`.

---

## Scenario Input

Runtime scenarios are stored externally under:

```text
data/scenarios/
```

A scenario follows the structure:

```json
{
  "scenario_id": "Example",
  "description": "Example runtime scenario.",
  "cycles": [
    {
      "cycle": 1,
      "snapshot": {
        "transport_type": "Patient_transport",
        "current_area": "Corridor",
        "vehicle_speed": 1.2,
        "speed_unit": "m/s",
        "age": 45,
        "heart_rate": 85,
        "heart_rate_unit": "bpm"
      }
    }
  ]
}
```

The scenario loader can load compatible scenario JSON files from a supplied path.

The current CLI exposes the predefined demonstrator scenarios through a small scenario registry.

---

## Running the Tests

Run the complete automated test suite:

```bash
python -m pytest
```

Run the static code checks:

```bash
ruff check .
```

The test suite covers:

- common data models;
- input handling;
- scene representation;
- ontology access;
- semantic mapping;
- Checking Conditions;
- overall assessment;
- monitoring output;
- end-to-end monitoring;
- execution traces;
- scenario loading and execution;
- demonstrator formatting;
- CLI execution.

---

## Pre-Runtime Configuration

The prototype separates static configuration from changing runtime input.

The main pre-runtime resources are:

```text
data/ontology/final_ontology.rdf
data/config/mapping_definitions.json
data/config/checking_conditions.json
data/config/response_rules.json
```

These resources are loaded before runtime and reused across monitoring cycles.

The scenario data itself is stored separately in:

```text
data/scenarios/
```

This separation allows runtime scenarios to be modified without changing the monitoring logic.

---

## Scope and Limitations

This repository contains a minimal research demonstrator, not a production or safety-certified monitoring system.

The prototype intentionally does not implement:

- live hospital sensor integration;
- temporal-history reasoning;
- prediction or trend analysis;
- complete ODD coverage;
- autonomous navigation;
- vehicle control;
- sensor fusion;
- clinical diagnosis;
- treatment recommendations;
- LLM-based semantic mapping;
- similarity-based ontology matching;
- runtime ontology modification.

The runtime data used by the demonstrator are synthetic.

The purpose of the implementation is to demonstrate the feasibility, separation of responsibilities, uncertainty handling, and traceability of the proposed monitoring concept.

---

## Academic Context

This repository accompanies a Forschungsarbeit at the University of Stuttgart on runtime monitoring of dynamic data within the Operational Design Domain of an Automated Patient Transport System.

The prototype implements a minimal end-to-end subset of the monitoring concept developed in the corresponding research work.

---

## Development Approach

The prototype was developed incrementally using:

- feature branches;
- modular implementation;
- unit tests;
- integration tests;
- end-to-end tests;
- static code checking with Ruff;
- task-level code reviews;
- Git version control.

A central implementation principle is separation of responsibilities:

```text
Scenario Loader
≠ Input Handler

Scene Representation
≠ Ontology

Semantic Mapping
≠ ODD Checking

Condition Results
≠ Overall Assessment

Overall Assessment
≠ Human Response

Formatter
≠ Monitoring Logic
```

This keeps the prototype traceable, testable, and easier to extend.

---

## Disclaimer

This repository is a research prototype intended for academic demonstration and evaluation.

It is not intended for clinical use, operational deployment, autonomous vehicle control, or safety-critical decision making.