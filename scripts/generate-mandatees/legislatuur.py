#!/usr/bin/env python3
from __future__ import print_function, unicode_literals
import datetime
from string import Template
from PyInquirer import prompt
from rdflib import Graph, Literal, URIRef
from validation import DateValidator, NumberValidator
from namespaces import *
from mu_sparql_helpers.escape_helpers import *
from mu_sparql_helpers.helpers import generate_uuid

GRAPH = "http://mu.semte.ch/graphs/public"
INVALIDATION_BASE_URI = "http://themis.vlaanderen.be/id/opheffing/"

################################################################################
### Legislatuur afsluiten
################################################################################

END_LEGISLATUUR_QUESTIONS = [
    {
        'type': 'input',
        'name': 'gov_body_uri',
        'message': "Wat is de uri van de te beëindigen legislatuur?",
    },
    {
        'type': 'input',
        'name': 'end_date',
        'message': "Wat is de eind-datum van de legislatuur?",
        'validate': DateValidator,
        'filter': datetime.date.fromisoformat
    },
]

def generate_end_legislatuur_query(gov_body_uri, end_date):
    end_datetime = datetime.datetime(end_date.year, end_date.month, end_date.day, tzinfo=datetime.timezone.utc)
    invalidation_uuid = generate_uuid()
    invalidation_uri = INVALIDATION_BASE_URI + invalidation_uuid
    query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX org: <http://www.w3.org/ns/org#>

DELETE {
    GRAPH $graph {
        $gov_body skos:prefLabel ?oldLabel .
    }
}
INSERT {
    GRAPH $graph {
        $gov_body skos:prefLabel ?newLabel ;
            prov:qualifiedInvalidation $invalidation .
        $invalidation a prov:Invalidation ;
            mu:uuid $invalidation_uuid ;
            prov:atTime ?end_date .
    }
}
WHERE {
    GRAPH $graph {
        $gov_body a besluit:Bestuursorgaan ;
            prov:qualifiedGeneration / prov:atTime ?start_date .
        $gov_body skos:prefLabel ?oldLabel .
        BIND(xsd:dateTime(?start_date) AS ?start_datetime)
        BIND(CONCAT(STR(DAY(?start_datetime)), "/", STR(MONTH(?start_datetime)), "/", STR(YEAR(?start_datetime))) AS ?label_start_date)
        BIND($end_datetime AS ?end_datetime)
        BIND(xsd:date(?end_datetime) AS ?end_date)
        BIND(CONCAT(STR(DAY(?end_datetime)), "/", STR(MONTH(?end_datetime)), "/", STR(YEAR(?end_datetime))) AS ?label_end_date)
        BIND(CONCAT("Vlaamse Regering ", ?label_start_date, " - ", ?label_end_date) AS ?newLabel)
    }
}

""")
    return query_template.substitute(
        graph=sparql_escape_uri(GRAPH),
        gov_body=sparql_escape_uri(gov_body_uri),
        invalidation=sparql_escape_uri(invalidation_uri),
        invalidation_uuid=sparql_escape_string(invalidation_uuid),
        end_datetime=sparql_escape_datetime(end_datetime)
    )

def ask_about_end_legislatuur():
    answers = prompt(END_LEGISLATUUR_QUESTIONS)
    query = generate_end_legislatuur_query(
        answers["gov_body_uri"],
        answers["end_date"])
    return query
