#!/usr/bin/env python3
import datetime
from string import Template
from pytz import timezone
from PyInquirer import prompt
from validation import DateValidator
from namespaces import *
from mu_sparql_helpers.escape_helpers import *
from mu_sparql_helpers.helpers import generate_uuid

BRUSSELS_TZ = timezone('Europe/Brussels')
GRAPH = "http://mu.semte.ch/graphs/public"

OPEN_GOV_BODY_IN_TIME_QUESTIONS = [

    {
        'type': 'input',
        'name': 'start_date',
        'message': "What's the government body start date?",
        'validate': DateValidator,
        'filter': datetime.date.fromisoformat
    },
    {
        'type': 'input',
        'name': 'government_body',
        'message': "What's the higher level government uri?",
    }
]

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
    end_datetime = datetime.datetime(end_date.year, end_date.month, end_date.day, tzinfo=BRUSSELS_TZ)
    INVALIDATION_BASE_URI = "http://themis.vlaanderen.be/id/opheffing/"
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
    
# <http://themis.vlaanderen.be/id/creatie/5fed907ee6670526694a06e2>	rdf:type	ns27:Generation ;
# 	ns3:uuid	"5fed907ee6670526694a06e2" ;
# 	ns27:atTime	"2019-07-02T00:00:00Z"^^xsd:dateTime .
# <http://themis.vlaanderen.be/id/opheffing/5fed907ee6670526694a06ff>	rdf:type	ns27:Invalidation ;
# 	ns3:uuid	"5fed907ee6670526694a06ff" ;
# 	ns27:atTime	"2019-10-02T00:00:00Z"^^xsd:dateTime .
# <http://themis.vlaanderen.be/id/rechtstreekse-verkiezing/5fed907de6670526694a04ea>	rdf:type	ns22:RechtstreekseVerkiezing ;
# 	ns3:uuid	"5fed907de6670526694a04ea" ;
# 	ns22:datum	"1995-05-21"^^xsd:date ;
# 	ns22:steltSamen	<http://themis.vlaanderen.be/id/bestuursorgaan/5fed907de6670526694a04e9> .
# <http://themis.vlaanderen.be/id/bestuursorgaan/5fed907de6670526694a04e9>	rdf:type	ns14:Bestuursorgaan ;
# 	ns3:uuid	"5fed907de6670526694a04e9" ;
# 	skos:prefLabel	"Vlaamse Regering 20/06/1995 - 12/07/1999" ;
# 	ns27:qualifiedGeneration	<http://themis.vlaanderen.be/id/creatie/5fed907de6670526694a052a> ;
# 	ns28:isTijdspecialisatieVan	<http://themis.vlaanderen.be/id/bestuursorgaan/7f2c82aa-75ac-40f8-a6c3-9fe539163025> ;
# 	ns27:qualifiedInvalidation	<http://themis.vlaanderen.be/id/opheffing/5fed907de6670526694a052b> ;
# 	ns16:hasPost	<http://themis.vlaanderen.be/id/mandaat/5fed907de6670526694a04ed> ,
# 		<http://themis.vlaanderen.be/id/mandaat/5fed907de6670526694a04eb> ,
# 		<http://themis.vlaanderen.be/id/mandaat/5fed907de6670526694a04ec> .
# 
# def generate_mandatee(title, person, start_date, end_date, rank, mandate):
#     g = Graph()
#     uuid = generate_uuid()
#     m = g.resource("{}id/mandatee/{}".format(THEMIS_BASE, uuid))
#     m.set(RDF.type, MANDAAT.Mandataris)
#     m.set(MU.uuid, Literal(uuid))
#     m.set(DCT.title, Literal(title))
#     m.set(MANDAAT.start, Literal(
#         datetime.datetime(start_date.year, start_date.month, start_date.day, tzinfo=BRUSSELS_TZ)))
#     if end_date:
#         m.set(MANDAAT.einde, Literal(
#         datetime.datetime(end_date.year, end_date.month, end_date.day, tzinfo=BRUSSELS_TZ)))
#     m.set(MANDAAT.rangorde, Literal(rank))
#     m.set(ORG.holds, URIRef(mandate))
#     m.set(MANDAAT.isBestuurlijkeAliasVan, URIRef(person))
#     return g


def ask_about_close_gov_body_in_time():
    answers = prompt(CLOSE_GOV_BODY_IN_TIME_QUESTIONS)
    query = generate_close_gov_body_in_time(
        answers["gov_body_uri"],
        answers["end_date"])
    return query