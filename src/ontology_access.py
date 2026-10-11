from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF

DEFAULT_ONTOLOGY_PATH = Path("data/ontology/final_ontology.rdf")
ONTOLOGY_NAMESPACE = Namespace(
    "http://www.semanticweb.org/tim/ontologies/2026/3/untitled-ontology-32#"
)

def build_ontology_uri(local_name: str) -> URIRef:
    return ONTOLOGY_NAMESPACE[local_name]

def load_ontology(
    ontology_path: Path = DEFAULT_ONTOLOGY_PATH,
) -> Graph:
    graph = Graph()
    graph.parse(ontology_path)

    return graph

def ontology_element_exists(
    graph: Graph,
    local_name: str,
) -> bool:
    element_uri = build_ontology_uri(local_name)

    return (
        (element_uri, None, None) in graph
        or (None, element_uri, None) in graph
        or (None, None, element_uri) in graph
    )

def get_ontology_types(
    graph: Graph,
    local_name: str,
) -> list[URIRef]:
    element_uri = build_ontology_uri(local_name)

    return list(
        graph.objects(
            subject=element_uri,
            predicate=RDF.type,
        )
    )


def get_ontology_element_type(
    graph: Graph,
    local_name: str,
) -> str | None:
    types = set(get_ontology_types(graph, local_name))

    if OWL.Class in types:
        return "Class"

    if OWL.NamedIndividual in types:
        return "NamedIndividual"

    if OWL.DatatypeProperty in types:
        return "DatatypeProperty"

    if OWL.ObjectProperty in types:
        return "ObjectProperty"

    if RDF.Property in types:
        return "RDFProperty"

    return None

def ontology_element_is_predicate(
    graph: Graph,
    local_name: str,
) -> bool:
    """Return whether the ontology URI occurs in predicate position."""
    element_uri = build_ontology_uri(local_name)
    # RDF triples follow Subject-Predicate-Object order. None acts as a
    # wildcard here, so this query asks whether element_uri occurs as Predicate.
    return (None, element_uri, None) in graph