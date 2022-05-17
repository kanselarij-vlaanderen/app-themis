#!/usr/bin/env python3
import datetime
from string import Template
from PyInquirer import prompt
from validation import DateValidator
from namespaces import *
from mu_sparql_helpers.escape_helpers import *
from mu_sparql_helpers.helpers import generate_uuid
from config import BRUSSELS_TZ, GRAPH, \
    REGERINGSSAMENSTELLING_BASE_URI, \
    INVALIDATION_BASE_URI, \
    GENERATION_BASE_URI

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
    end_datetime = datetime.datetime(end_date.year, end_date.month, end_date.day, tzinfo=BRUSSELS_TZ)
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

DELETE {
    GRAPH $graph {
        ?mandatee mandaat:einde ?mandatee_end .
    }
}
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
        OPTIONAL { ?mandatee mandaat:einde ?mandatee_end . }
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
    start_datetime = datetime.datetime(start_date.year,
        start_date.month,
        start_date.day,
        tzinfo=BRUSSELS_TZ)

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
