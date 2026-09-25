# APTS ODD Monitoring Prototype

## Project Overview

This project implements a minimal Python prototype for runtime monitoring of selected
dynamic and contextual information within the Operational Design Domain (ODD) of an
Autonomous Patient Transport System (APTS).

The prototype is part of a Forschungsarbeit at the University of Stuttgart.

Its purpose is to demonstrate the end-to-end processing chain:

Runtime Input
→ Scene Representation
→ Semantic Mapping
→ ODD Conformity Checking
→ Overall Assessment
→ Monitoring Output

The prototype is intended as a research demonstrator and not as a production,
clinical, or safety-certified system.

## Core Monitoring Elements

The minimal prototype uses the following representative runtime information:

- Patient transport type
- Current area
- Vehicle speed
- Surface condition
- Age as contextual information
- Heart rate

## Assessment States

The prototype distinguishes three overall assessment states:

- Inside ODD
- Outside ODD
- Unclear

Individual checking conditions produce:

- Satisfied
- Violated
- Unresolved

## Technology

- Python 3.10
- RDF / OWL ontology
- RDFLib for ontology access
- JSON configuration files
- pytest for automated testing

## Project Structure

```text
apts_odd_prototype/
├── data/
│   ├── config/
│   ├── ontology/
│   └── scenarios/
├── src/
├── tests/
├── README.md
├── requirements.txt
└── prototype_decision_log.md