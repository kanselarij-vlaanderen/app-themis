#!/usr/bin/env python3
import datetime
from string import Template
from rdflib import Graph
from PyInquirer import prompt
from validation import DateValidator
from namespaces import *
from mu_sparql_helpers.escape_helpers import *
from mu_sparql_helpers.helpers import generate_uuid
from config import BRUSSELS_TZ, GRAPH, \
    REGERINGSSAMENSTELLING_BASE_URI, \
    INVALIDATION_BASE_URI, \
    GENERATION_BASE_URI, \
    VLAAMSE_REGERING, \
    MANDATEE_TTL_DATASET_FILE

################################################################################
### Regeringsamenstelling afsluiten
################################################################################

END_REGERINGSSAMENSTELLING_QUESTIONS = [
    {
        'type': 'input',
        'name': 'gov_body_uri',
        'message': "Wat is de URI van de af te sluiten regeringssamenstelling?",
    },
    {
        'type': 'input',
        'name': 'end_date',
        'message': "Wat is de einddatum?",
        'validate': DateValidator,
        'filter': datetime.date.fromisoformat
    },
]

def generate_end_regeringssamenstelling_query(gov_body_uri, end_date):
    end_datetime = BRUSSELS_TZ.localize(datetime.datetime(end_date.year, end_date.month, end_date.day))
    invalidation_uuid = generate_uuid()
    invalidation_uri = INVALIDATION_BASE_URI + invalidation_uuid
    query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX org: <http://www.w3.org/ns/org#>
PREFIX prov: <http://www.w3.org/ns/prov#>

INSERT {
    GRAPH $graph {
        $gov_body prov:qualifiedInvalidation $invalidation .
        $invalidation a prov:Invalidation ;
            mu:uuid $invalidation_uuid ;
            prov:atTime $end_datetime .
    }
}
WHERE {
    GRAPH $graph {
        $gov_body a besluit:Bestuursorgaan .
    }
}
;

INSERT {
    GRAPH $graph {
        ?mandatee mandaat:einde $end_datetime .
    }
}
WHERE {
    GRAPH $graph {
        $gov_body a besluit:Bestuursorgaan ;
            prov:hadMember ?mandatee .
        ?mandatee a mandaat:Mandataris .
        FILTER NOT EXISTS { ?mandatee mandaat:einde ?mandatee_end . }
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

def ask_about_end_regeringssamenstelling():
    g = Graph()
    g.parse(MANDATEE_TTL_DATASET_FILE)
    qres = g.query(generate_current_regeringssamenstelling_query())
    for res in qres:  # only iterates max once (not an iterator, no decent other way)
        print(f"De actieve regeringssamenstelling volgens aangeleverde dump is {res.samenstelling} ({res.label}).")
        END_REGERINGSSAMENSTELLING_QUESTIONS[0]["default"] = res.samenstelling
        answers = prompt(END_REGERINGSSAMENSTELLING_QUESTIONS)
        query = generate_end_regeringssamenstelling_query(
            answers["gov_body_uri"],
            answers["end_date"])
        return query

################################################################################
### Regeringsamenstelling starten
################################################################################

START_REGERINGSSAMENSTELLING_QUESTIONS = [
    {
        'type': 'input',
        'name': 'legislatuur_uri',
        'message': "Wat is de URI van de gerelateerde legislatuur?",
    },
    {
        'type': 'input',
        'name': 'label',
        'message': "Wat is de naam van deze regeringssamenstelling? (bv. 'Peeters II')",
    },
    {
        'type': 'input',
        'name': 'start_date',
        'message': "Wat is de startdatum?",
        'validate': DateValidator,
        'filter': datetime.date.fromisoformat
    },
]

def generate_start_regeringssamenstelling_query(legislatuur_uri, label, start_date):
    start_datetime = BRUSSELS_TZ.localize(datetime.datetime(start_date.year,
        start_date.month,
        start_date.day))

    samenstelling_uuid = generate_uuid()
    samenstelling_uri = REGERINGSSAMENSTELLING_BASE_URI + samenstelling_uuid

    generation_uuid = generate_uuid()
    generation_uri = GENERATION_BASE_URI + generation_uuid

    query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX generiek: <https://data.vlaanderen.be/ns/generiek#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

INSERT {
    GRAPH $graph {
        $samenstelling a besluit:Bestuursorgaan ;
            mu:uuid $samenstelling_uuid ;
            skos:prefLabel $label ;
            generiek:isTijdspecialisatieVan $legislatuur ;
            prov:qualifiedGeneration $generation .
        $generation a prov:Generation ;
            mu:uuid $generation_uuid ;
            prov:atTime $start_datetime .
    }
}
WHERE {
    GRAPH $graph {
        $legislatuur a besluit:Bestuursorgaan .
    }
}

""")
    return query_template.substitute(
        graph=sparql_escape_uri(GRAPH),
        samenstelling=sparql_escape_uri(samenstelling_uri),
        samenstelling_uuid=sparql_escape_string(samenstelling_uuid),
        label=sparql_escape_string(label),
        legislatuur=sparql_escape_uri(legislatuur_uri),
        generation=sparql_escape_uri(generation_uri),
        generation_uuid=sparql_escape_string(generation_uuid),
        start_datetime=sparql_escape_datetime(start_datetime)
    )

def ask_about_start_regeringssamenstelling():
    answers = prompt(START_REGERINGSSAMENSTELLING_QUESTIONS)
    query = generate_start_regeringssamenstelling_query(
        answers["legislatuur_uri"],
        answers["label"],
        answers["start_date"])
    return query

################################################################################
### Huidige regeringsamenstelling bevragen
################################################################################

CURRENT_REGERINGSSAMENSTELLING_QUESTION = [
    {
        'type': 'input',
        'name': 'samenstelling_uri',
        'message': "Wat is de URI van de huidige regerinssamenstelling?",
    },
]

def generate_current_regeringssamenstelling_query():
    query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX generiek: <https://data.vlaanderen.be/ns/generiek#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?samenstelling ?label
WHERE {
    ?samenstelling a besluit:Bestuursorgaan ;
        skos:prefLabel ?label ;
        generiek:isTijdspecialisatieVan / generiek:isTijdspecialisatieVan $vr ;
        prov:qualifiedGeneration ?generation .
    ?generation a prov:Generation ;
        prov:atTime ?start_datetime .
    FILTER NOT EXISTS { ?samenstelling prov:qualifiedInvalidation ?invalidation }
}
ORDER BY DESC(?start_datetime)
LIMIT 1
""")
    return query_template.substitute(
        vr=sparql_escape_uri(VLAAMSE_REGERING),
    )

def ask_about_current_regeringssamenstelling():
    g = Graph()
    g.parse(MANDATEE_TTL_DATASET_FILE)
    qres = g.query(generate_current_regeringssamenstelling_query())
    for res in qres:  # only iterates max once (not an iterator, no decent other way)
        print(f"De actieve regeringssamenstelling volgens aangeleverde dump is {res.samenstelling} ({res.label}).")
        CURRENT_REGERINGSSAMENSTELLING_QUESTION[0]["default"] = res.samenstelling
        answers = prompt(CURRENT_REGERINGSSAMENSTELLING_QUESTION)
        return answers["samenstelling_uri"]
