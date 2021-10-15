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

CLOSE_GOV_BODY_IN_TIME_QUESTIONS = [
    {
        'type': 'input',
        'name': 'gov_body_uri',
        'message': "What's the gov body in time uri?",
    },
    {
        'type': 'input',
        'name': 'end_date',
        'message': "What's the government body end date?",
        'validate': DateValidator,
        'filter': datetime.date.fromisoformat
    },
]

def generate_close_gov_body_in_time(gov_body_uri, end_date):
    end_datetime = datetime.datetime(end_date.year, end_date.month, end_date.day, tzinfo=datetime.timezone.utc)
    INVALIDATION_BASE_URI = "http://themis.vlaanderen.be/id/opheffing/"
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

def ask_about_close_gov_body_in_time():
    answers = prompt(CLOSE_GOV_BODY_IN_TIME_QUESTIONS)
    query = generate_close_gov_body_in_time(
        answers["gov_body_uri"],
        answers["end_date"])
    return query