#!/usr/bin/env python3
from __future__ import print_function, unicode_literals
import datetime
from uuid import uuid4 as generate_uuid
from pytz import timezone
from PyInquirer import prompt
from rdflib import Graph, Literal, URIRef
from validation import DateValidator, NumberValidator
from namespaces import *

BRUSSELS_TZ = timezone('Europe/Brussels')

MP = "https://themis.vlaanderen.be/id/bestuursfunctie/5fed907ce6670526694a03de"
VICE_MP = "http://themis.vlaanderen.be/id/bestuursfunctie/5fed907ce6670526694a03df"
MINISTER = "http://themis.vlaanderen.be/id/bestuursfunctie/5fed907ce6670526694a03e0"

BESTUURSFUNCTIES = [
    MP,
    VICE_MP,
    MINISTER
]

MANDATEE_QUESTIONS = [
    {
        'type': 'input',
        'name': 'title',
        'message': "What's the mandatees official title?",
    },
    {
        'type': 'input',
        'name': 'start_date',
        'message': "What's the mandatees start date?",
        'validate': DateValidator,
        'filter': datetime.date.fromisoformat
    },
    {
        'type': 'input',
        'name': 'end_date',
        'message': "What's the mandatees end date?",
        # 'validate': DateValidator,
        'filter': lambda d: datetime.date.fromisoformat if d else None
    },
    {
        'type': 'input',
        'name': 'rank',
        'message': "What's the mandatees rank?",
        'validate': NumberValidator,
        'filter': int
    },
    {
        'type': 'input',
        'name': 'person',
        'message': "What's the mandatees related person uri?",
    },
    {
        'type': 'input',
        'name': 'mandate',
        'message': "What's the mandatees related mandate uri?",
    }
]



def generate_mandatee(title, person, start_date, end_date, rank, mandate, regeringssamenstelling):
    g = Graph()
    uuid = generate_uuid()
    m = g.resource("{}id/mandatee/{}".format(THEMIS_BASE, uuid))
    m.set(RDF.type, MANDAAT.Mandataris)
    m.set(MU.uuid, Literal(uuid))
    if title:
        m.set(DCT.title, Literal(title))
    m.set(MANDAAT.start, Literal(
        datetime.datetime(start_date.year, start_date.month, start_date.day, tzinfo=BRUSSELS_TZ)))
    if end_date:
        m.set(MANDAAT.einde, Literal(
        datetime.datetime(end_date.year, end_date.month, end_date.day, tzinfo=BRUSSELS_TZ)))
    m.set(MANDAAT.rangorde, Literal(rank))
    m.set(ORG.holds, URIRef(mandate))
    m.set(MANDAAT.isBestuurlijkeAliasVan, URIRef(person))
    g.add((URIRef(regeringssamenstelling), PROV.hadMember, m.identifier))
    return g


def ask_about_mandatee(regeringssamenstelling):
    answers = prompt(MANDATEE_QUESTIONS)
    graph = generate_mandatee(
        answers["title"],
        answers["person"],
        answers["start_date"],
        answers["end_date"],
        answers["rank"],
        answers["mandate"],
        regeringssamenstelling)
    return graph

def mandatee_generation_loop(regeringssamenstelling):
    g = Graph()
    while True:
        again = prompt([{
            "type": "confirm",
            "name": "confirmation",
            "message": f"(Nog) een nieuwe mandataris aanmaken?",
            "default": True
        }])["confirmation"]
        if not again:
            break
        g = g + ask_about_mandatee(regeringssamenstelling)
    return g
