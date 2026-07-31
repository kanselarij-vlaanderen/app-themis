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

def duplicate_mandatees(regeringssamenstelling, start_date_default, new_end=None):
    g = Graph()
    g.parse(MANDATEE_TTL_DATASET_FILE)
    qres = g.query(current_mandatees_query.substitute(samenstelling=f"<{regeringssamenstelling}>"))
    new_g = Graph()
    renewals = []
    for row in qres:
        pick_mandatee = prompt([{
            "type": "confirm",
            "name": "confirmation",
            "message": f"New mandatee based on {row.familyName} - {row.title} ({row.mandateLabel})",
            "default": True
        }])["confirmation"]
        if pick_mandatee:
            questions = copy.deepcopy(MANDATEE_QUESTIONS)
            if row.title:
                questions[0]["default"] = row.title
            questions[1]["default"] = start_date_default.isoformat()[0:10]
            # questions[2]["default"] = end_date
            questions[3]["default"] = row.order
            questions[5]["default"] = row.mandate
            questions.pop(4) # The person stays the same
            answers = prompt(questions)

            end_date = answers["start_date"] # end date of the old mandatee = start date of the new mandatee
            mandatee_g = generate_mandatee(
                answers["title"],
                row.person,
                answers["start_date"],
                None,
                answers["rank"],
                answers["mandate"],
                regeringssamenstelling)
            renewals.append({
                "old": str(row.mandatee),
                "new": str(next(mandatee_g.subjects(RDF.type, MANDAAT.Mandataris))),
                "name": str(row.familyName),
                "title": answers["title"]
            })
            new_g = new_g + mandatee_g # merge graphs
            print("[OK]")
        else:
            end_date = start_date_default
            print(("Warning: no new mandatee based on {}. "
                "The end date is set to the current date ({}) "
                "and will probably need adjusting.").format(
                row.familyName, start_date_default.isoformat()[0:10]))
        new_g.add([
            URIRef(row.mandatee),
            MANDAAT.einde,
            Literal(BRUSSELS_TZ.localize(datetime.datetime(end_date.year, end_date.month, end_date.day)))
        ])
    return new_g, renewals

