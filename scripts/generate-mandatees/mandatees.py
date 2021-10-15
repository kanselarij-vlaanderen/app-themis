#!/usr/bin/env python3
from __future__ import print_function, unicode_literals
import datetime
from uuid import uuid4 as generate_uuid
from PyInquirer import prompt
from rdflib import Graph, Literal, URIRef
from validation import DateValidator, NumberValidator
from namespaces import *

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
        'validate': DateValidator,
        'filter': datetime.date.fromisoformat
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



def generate_mandatee(title, person, start_date, end_date, rank, mandate):
    g = Graph()
    uuid = generate_uuid()
    m = g.resource("{}id/mandatee/{}".format(THEMIS_BASE, uuid))
    m.set(RDF.type, MANDAAT.Mandataris)
    m.set(MU.uuid, Literal(uuid))
    m.set(DCT.title, Literal(title))
    m.set(MANDAAT.start, Literal(
        datetime.datetime(start_date.year, start_date.month, start_date.day, tzinfo=datetime.timezone.utc)))
    if end_date:
        m.set(MANDAAT.einde, Literal(
        datetime.datetime(end_date.year, end_date.month, end_date.day, tzinfo=datetime.timezone.utc)))
    m.set(MANDAAT.rangorde, Literal(rank))
    m.set(ORG.holds, URIRef(mandate))
    m.set(MANDAAT.isBestuurlijkeAliasVan, URIRef(person))
    return g


def ask_about_mandatee():
    answers = prompt(MANDATEE_QUESTIONS)
    graph = generate_mandatee(
        answers["title"],
        answers["person"],
        answers["start_date"],
        answers["end_date"],
        answers["rank"],
        answers["mandate"])
    return graph