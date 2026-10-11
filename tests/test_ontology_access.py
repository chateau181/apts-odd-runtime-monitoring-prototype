from rdflib.namespace import OWL

from src.ontology_access import (
    build_ontology_uri,
    get_ontology_element_type,
    get_ontology_types,
    load_ontology,
    ontology_element_exists,
    ontology_element_is_predicate,
)


def test_load_ontology():
    graph = load_ontology()

    assert len(graph) == 1530

def test_existing_ontology_element_is_found():
    graph = load_ontology()

    assert ontology_element_exists(graph, "Wet") is True

def test_unknown_ontology_element_is_not_found():
    graph = load_ontology()

    assert ontology_element_exists(
        graph,
        "DefinitelyNotAnOntologyElement",
    ) is False

def test_get_types_for_wet():
    graph = load_ontology()

    types = get_ontology_types(graph, "Wet")

    assert OWL.NamedIndividual in types

def test_get_types_for_corridor():
    graph = load_ontology()

    types = get_ontology_types(graph, "Corridor")

    assert OWL.Class in types

def test_has_heart_frequency_exists_without_formal_rdf_type():
    graph = load_ontology()

    assert ontology_element_exists(
        graph,
        "hasHeartFrequency",
    ) is True

    types = get_ontology_types(
        graph,
        "hasHeartFrequency",
    )

    assert types == []

def test_wet_element_type_is_named_individual():
    graph = load_ontology()

    assert (
        get_ontology_element_type(graph, "Wet")
        == "NamedIndividual"
    )


def test_corridor_element_type_is_class():
    graph = load_ontology()

    assert get_ontology_element_type(graph, "Corridor") == "Class"


def test_speed_value_element_type_is_datatype_property():
    graph = load_ontology()

    assert (
        get_ontology_element_type(graph, "speedValue")
        == "DatatypeProperty"
    )


def test_untyped_heart_frequency_has_no_element_type():
    graph = load_ontology()

    assert (
        get_ontology_element_type(graph, "hasHeartFrequency")
        is None
    )

def test_build_ontology_uri():
    uri = build_ontology_uri("Wet")

    assert str(uri) == (
        "http://www.semanticweb.org/tim/ontologies/"
        "2026/3/untitled-ontology-32#Wet"
    )

def test_has_heart_frequency_is_used_as_predicate():
    graph = load_ontology()

    assert ontology_element_is_predicate(
        graph,
        "hasHeartFrequency",
    )

def test_wet_is_not_used_as_predicate():
    graph = load_ontology()

    assert not ontology_element_is_predicate(
        graph,
        "Wet",
    )