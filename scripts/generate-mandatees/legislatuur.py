#!/usr/bin/env python3
from __future__ import print_function, unicode_literals
import datetime
from string import Template
from PyInquirer import prompt
from validation import DateValidator
from namespaces import *
from mu_sparql_helpers.escape_helpers import *
from mu_sparql_helpers.helpers import generate_uuid
from config import BRUSSELS_TZ
from mandatees import BESTUURSFUNCTIES

GRAPH = "http://mu.semte.ch/graphs/public"

LEGISLATUUR_BASE_URI = "http://themis.vlaanderen.be/id/bestuursorgaan/"
MANDAAT_BASE_URI = "http://themis.vlaanderen.be/id/mandaat/"
INVALIDATION_BASE_URI = "http://themis.vlaanderen.be/id/opheffing/"
GENERATION_BASE_URI = "http://themis.vlaanderen.be/id/creatie/"

VLAAMSE_REGERING = "http://themis.vlaanderen.be/id/bestuursorgaan/7f2c82aa-75ac-40f8-a6c3-9fe539163025"



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
    end_datetime = datetime.datetime(end_date.year, end_date.month, end_date.day, tzinfo=BRUSSELS_TZ)
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

################################################################################
### Legislatuur starten
################################################################################

START_LEGISLATUUR_QUESTIONS = [
    {
        'type': 'input',
        'name': 'start_date',
        'message': "Wat is de start-datum van de legislatuur?",
        'validate': DateValidator,
        'filter': datetime.date.fromisoformat
    },
]

def generate_mandaten_query(legislatuur_uri):
    query_string = """
PREFIX org: <http://www.w3.org/ns/org#>
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>

INSERT DATA {
    GRAPH $graph {
""".replace("$graph", sparql_escape_uri(GRAPH))
    for functie in BESTUURSFUNCTIES:
        uuid = generate_uuid()
        uri =  MANDAAT_BASE_URI + uuid
        query_string += Template("""
        $mandaat a mandaat:Mandaat ;
        	mu:uuid	$uuid ;
        	org:role $functie .
        $legislatuur org:hasPost $mandaat .""").substitute(
    mandaat=sparql_escape_uri(uri),
    uuid=sparql_escape_string(uuid),
    functie=sparql_escape_uri(functie),
    legislatuur=sparql_escape_uri(legislatuur_uri))
    query_string += """
    }
}"""
    return query_string

def generate_start_legislatuur_query(start_date):
    start_datetime = datetime.datetime(start_date.year,
        start_date.month,
        start_date.day,
        tzinfo=BRUSSELS_TZ)

    legislatuur_uuid = generate_uuid()
    legislatuur_uri = LEGISLATUUR_BASE_URI + legislatuur_uuid

    generation_uuid = generate_uuid()
    generation_uri = GENERATION_BASE_URI + generation_uuid

    label = "Vlaamse Regering {} - ...".format(start_date.strftime("%d/%m/%Y"))

    query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX generiek: <https://data.vlaanderen.be/ns/generiek#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

INSERT DATA {
    GRAPH $graph {
        $legislatuur a besluit:Bestuursorgaan ;
            mu:uuid $legislatuur_uuid ;
            skos:prefLabel $label ;
            generiek:isTijdspecialisatieVan $regering ;
            prov:qualifiedGeneration $generation .
        $generation a prov:Generation ;
            mu:uuid $generation_uuid ;
            prov:atTime $start_datetime .
    }
}
""")

    query_string = query_template.substitute(
        graph=sparql_escape_uri(GRAPH),
        legislatuur=sparql_escape_uri(legislatuur_uri),
        legislatuur_uuid=sparql_escape_string(legislatuur_uuid),
        label=sparql_escape_string(label),
        regering=sparql_escape_uri(VLAAMSE_REGERING),
        generation=sparql_escape_uri(generation_uri),
        generation_uuid=sparql_escape_string(generation_uuid),
        start_datetime=sparql_escape_datetime(start_datetime)
    )
    query_string += ";"
    query_string += generate_mandaten_query(legislatuur_uri)
    return query_string

def ask_about_start_legislatuur():
    answers = prompt(START_LEGISLATUUR_QUESTIONS)
    query = generate_start_legislatuur_query(answers["start_date"])
    return query
