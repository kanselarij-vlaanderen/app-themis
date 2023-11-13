#!/usr/bin/env python3
import datetime
import copy
from string import Template
from PyInquirer import prompt
from rdflib import Graph, Literal, URIRef
from namespaces import *
from config import BRUSSELS_TZ, MANDATEE_TTL_DATASET_FILE
from mandatees import MANDATEE_QUESTIONS, generate_mandatee


current_mandatees_query = Template("""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX person: <http://www.w3.org/ns/person#>
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX org: <http://www.w3.org/ns/org#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT ?mandatee ?person ?familyName ?mandate ?mandateLabel ?order ?title
WHERE {
    $samenstelling prov:hadMember ?mandatee .
    ?mandatee
        a mandaat:Mandataris ;
        mandaat:isBestuurlijkeAliasVan ?person ;
        mandaat:start ?mandatee_start ;
        mandaat:rangorde ?order ;
        org:holds ?mandate .
    ?mandate org:role / skos:prefLabel ?mandateLabel
  	OPTIONAL { ?mandatee dct:title ?title }
    ?person
        a person:Person ;
        foaf:familyName ?familyName .
        FILTER NOT EXISTS { ?mandatee mandaat:einde ?mandatee_end }
 }
ORDER BY ?order
""")

# Originally this query contained a `UNION` of FILTER NOT EXISTS with
# UNION 
# {
#     ?mandatee mandaat:einde ?mandatee_end .
#     FILTER(?mandatee_end > NOW())
# }
# Since it seems like the sparql interpreter doesn't like the union + w don't have that case in practice
# in data atm, it is left out for now

def duplicate_mandatees(regeringssamenstelling, new_start, new_end=None):
    g = Graph()
    g.parse(MANDATEE_TTL_DATASET_FILE)
    qres = g.query(current_mandatees_query.substitute(samenstelling=f"<{regeringssamenstelling}>"))
    new_g = Graph()
    for row in qres:
        pick_mandatee = prompt([{
            "type": "confirm",
            "name": "confirmation",
            "message": f"New mandatee based on {row.familyName} - {row.title} ({row.mandateLabel})",
            "default": True
        }])["confirmation"]
        new_g.add([
            URIRef(row.mandatee),
            MANDAAT.einde,
            Literal(BRUSSELS_TZ.localize(datetime.datetime(new_start.year, new_start.month, new_start.day)))
        ]) # Assumes all mandatees get "renewed" once there is one change
        if not pick_mandatee:
            continue

        questions = copy.deepcopy(MANDATEE_QUESTIONS)
        if row.title:
            questions[0]["default"] = row.title
        questions[1]["default"] = new_start.isoformat()[0:10]
        # questions[2]["default"] = end_date
        questions[3]["default"] = row.order
        questions[5]["default"] = row.mandate
        questions.pop(4) # The person stays the same
        answers = prompt(questions)

        new_g = new_g + generate_mandatee( # merge graphs
            answers["title"],
            row.person,
            answers["start_date"],
            None,
            answers["rank"],
            answers["mandate"],
            regeringssamenstelling)
        print("[OK]")
    return new_g

