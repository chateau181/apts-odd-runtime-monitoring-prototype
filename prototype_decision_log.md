# Prototype Decision Log

This document records important design and implementation decisions for the
APTS ODD Monitoring Prototype.

The purpose is to preserve traceability between the accepted research concept,
prototype implementation, and later evaluation.

---

## D-001 — Programming Language

**Decision:** Use Python 3.10.

**Reason:**  
Python provides suitable support for structured data processing, RDF/OWL access,
configuration handling, testing, and rapid implementation of a research prototype.

**Status:** Accepted

---

## D-002 — Ontology Access Library

**Decision:** Use RDFLib for programmatic access to the RDF/OWL ontology.

**Reason:**  
RDFLib provides lightweight RDF graph loading, inspection, and querying without
requiring a database or separate ontology server.

**Status:** Accepted

---

## D-003 — Frozen Ontology Baseline

**Decision:** Use the originally analysed `final_ontology.rdf` as the read-only
semantic reference for the prototype.

**Reason:**  
The Conception and Evaluation Specification were completed and accepted based on
this ontology version. Retaining it preserves consistency and traceability between
the research documents and the prototype.

**Consequence:**  
The ontology is not modified during prototype development or runtime monitoring.

**Status:** Frozen

---

## D-004 — Runtime Scene Representation

**Decision:** Represent runtime information independently from the ontology.

**Reason:**  
Runtime information must remain available even if semantic mapping is unsuccessful.

**Consequence:**  
Scene Elements and Mapping Results are implemented as separate data structures.

**Status:** Frozen

---

## D-005 — Semantic Mapping

**Decision:** Use deterministic, predefined semantic mappings.

**Reason:**  
The minimal prototype requires transparent and reproducible mapping behaviour.

**Consequence:**  
No LLM-based, similarity-based, or automatic ontology matching is used.

**Status:** Frozen

---

## D-006 — Checking Conditions

**Decision:** Keep operational Checking Conditions separate from ontology semantics.

**Reason:**  
The existing ontology provides semantic representation but does not encode all
required operational thresholds and conformity rules.

**Consequence:**  
Checking rules are defined separately from the RDF ontology.

**Status:** Frozen

---

## D-007 — Overall Assessment

**Decision:** Use the three overall assessment states:

- Inside ODD
- Outside ODD
- Unclear

Condition-level results are:

- Satisfied
- Violated
- Unresolved

**Aggregation rule:**

- all applicable conditions Satisfied → Inside ODD
- at least one Violated → Outside ODD
- no Violated and at least one Unresolved → Unclear

A Violated condition has precedence over Unresolved conditions, while unresolved
reasons remain visible in the monitoring result.

**Status:** Frozen

---

## D-008 — Dynamic Monitoring

**Decision:** Implement dynamic monitoring as repeated assessment of runtime snapshots.

**Reason:**  
This is sufficient for the minimal demonstrator and preserves the defined runtime
monitoring workflow.

**Consequence:**  
Each cycle is evaluated independently through the same monitoring pipeline.

No history-based temporal reasoning, prediction, or trend detection is implemented.

**Status:** Frozen

---

## D-009 — Core Prototype Elements

**Decision:** Use the following representative Scene Elements:

- `Patient_transport`
- `Corridor`
- vehicle speed
- surface condition
- age
- heart rate

**Reason:**  
These elements cover contextual, numerical, environmental, and patient-related
runtime information while keeping the prototype minimal.

**Status:** Frozen

---

## D-010 — Heart Rate Mapping

**Decision:** Map runtime Heart Rate through a predefined structured mapping to the
existing ontology reference `hasHeartFrequency`.

**Reason:**  
The original ontology contains an existing heart-frequency semantic reference but
does not provide a complete formal Heart Rate model.

**Consequence:**  
The ontology remains unchanged. Heart Rate checking is performed using an external
Checking Condition.

**Status:** Frozen

---

## D-011 — Configuration

**Decision:** Store semantic mapping definitions and Checking Conditions in external
JSON configuration files.

**Reason:**  
Configuration should remain separate from Python processing logic so that mappings
and checking rules can be changed without modifying unrelated code.

**Status:** Planned

---

## D-012 — Testing

**Decision:** Use pytest for automated module and pipeline testing.

**Reason:**  
Automated tests provide repeatable evidence that implemented behaviour matches the
defined monitoring semantics and evaluation cases.

**Status:** Accepted