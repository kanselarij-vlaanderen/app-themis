#!/usr/bin/env python3
import os
from string import Template
from rdflib import Graph, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from namespaces import ORG
from config import SPARQL_ENDPOINT, MIGRATIONS_FOLDER, GRAPH

KABINET_OF_MANDATEE_QUERY = Template("""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX org: <http://www.w3.org/ns/org#>

SELECT DISTINCT ?kabinet ?label
WHERE {
    ?kabinet a foaf:Organization ;
        skos:prefLabel ?label ;
        org:hasMember $mandatee .
}
""")

ALL_KABINETTEN_QUERY = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX org: <http://www.w3.org/ns/org#>

SELECT DISTINCT ?kabinet ?label ?ovoCode
WHERE {
    ?kabinet a foaf:Organization ;
        skos:prefLabel ?label .
    OPTIONAL { ?kabinet org:identifier ?ovoCode }
    FILTER(STRSTARTS(STR(?label), "Kabinet"))
}
ORDER BY ?label
"""


def generate_kabinet_memberships(renewals):
    """Look up the kabinet of every renewed mandatee's old mandataris in Virtuoso
    and generate an org:hasMember triple for the new mandataris (the person, and
    thus the kabinet, stays the same). Returns (graph, resolved, unresolved)."""
    db = Graph(SPARQLStore(query_endpoint=SPARQL_ENDPOINT))
    g = Graph()
    resolved = []
    unresolved = []
    for renewal in renewals:
        found = False
        for row in db.query(KABINET_OF_MANDATEE_QUERY.substitute(mandatee="<{}>".format(renewal["old"]))):
            g.add((URIRef(row.kabinet), ORG.hasMember, URIRef(renewal["new"])))
            resolved.append(dict(renewal, kabinet=str(row.kabinet), kabinet_label=str(row.label)))
            found = True
        if not found:
            unresolved.append(renewal)
    return g, resolved, unresolved


def print_manual_kabinet_instructions(mandatees):
    print("\nThe following new mandatees have to be added to their kabinet manually (org:hasMember):")
    for m in mandatees:
        print("  - <{}> ({})".format(m["new"], m.get("title") or m.get("name") or "no title"))
    print("\nExample migration content:")
    print("    @prefix org: <http://www.w3.org/ns/org#> .")
    for m in mandatees:
        print("    <kabinet-uri-here> org:hasMember <{}> .".format(m["new"]))
    try:
        db = Graph(SPARQLStore(query_endpoint=SPARQL_ENDPOINT))
        kabinetten = list(db.query(ALL_KABINETTEN_QUERY))
        if kabinetten:
            print("\nKabinetten currently known in Virtuoso:")
            for row in kabinetten:
                print("  - {} ({}): {}".format(row.label, row.ovoCode or "no OVO code", row.kabinet))
    except (OSError, ValueError):
        print("\n(The known kabinetten can't be listed since Virtuoso isn't reachable.)")


def handle_kabinet_memberships(renewals, new_mandatees, timestamp):
    """Write an org:hasMember migration for the kabinet memberships that can be
    derived automatically and print manual instructions for the rest."""
    unresolved = []
    try:
        g, resolved, unresolved = generate_kabinet_memberships(renewals)
        for r in resolved:
            print("Kabinet membership generated: {} -> new mandataris of {}".format(r["kabinet_label"], r["name"]))
        if len(g):
            filename = MIGRATIONS_FOLDER + "{}-kabinet-members.ttl".format(timestamp)
            g.serialize(destination=filename, format="turtle")
            with open(filename.replace(".ttl", ".graph"), "w") as f:
                f.write(GRAPH)
            print("Wrote kabinet memberships migration to {} (+ graph file)".format(os.path.relpath(filename, "/data/app")))
    except (OSError, ValueError) as e:
        # rdflib's SPARQLConnector re-raises connection errors as ValueError
        e = e.__context__ or e
        print("Warning: failed to query Virtuoso for kabinetten ({}).".format(e))
        unresolved = list(renewals)
    unresolved = unresolved + list(new_mandatees)
    if unresolved:
        print_manual_kabinet_instructions(unresolved)
