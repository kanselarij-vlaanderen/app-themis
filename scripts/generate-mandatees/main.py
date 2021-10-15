#!/usr/bin/env python3
from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
from uuid import uuid4 as generate_uuid
from rdflib import Graph, Namespace, Literal, URIRef
from prompt_toolkit.validation import Validator, ValidationError
from validation import DateValidator, NumberValidator
import datetime
from generate_government_body import ask_about_close_gov_body_in_time, ask_about_end_legislatuur

MIGRATIONS_FOLDER = "/data/app/config/migrations/"

questions = [
    {
        'type': 'list',
        'name': 'flowType',
        'message': 'Wat wil u doen?',
        'choices': [
            {
                'name': 'Een regering afsluiten',
            },
            {
                'name': 'Een legislatuur afsluiten',
            },
            {
                'name': 'Een nieuwe regering (binnen een lopende legislatuur) starten',
            },
            {
                'name': 'Een nieuwe legislatuur (inclusief eerste regering) starten',
            }
        ]
    }
]


answers = prompt(questions)
flow_type = answers["flowType"]

if flow_type == "Een regering afsluiten":
    query_string = ask_about_close_gov_body_in_time()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = MIGRATIONS_FOLDER + "{}-close-gov-body.sparql".format(timestamp)
    with open(filename, "w") as f:
        f.write(query_string)
elif flow_type == "Een legislatuur afsluiten":
    query_string = ask_about_end_legislatuur()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = MIGRATIONS_FOLDER + "{}-end-legislatuur.sparql".format(timestamp)
    with open(filename, "w") as f:
        f.write(query_string)
    print("Het beëindigen van een legislatuur houdt normaal gezien ook het beëindigen van de laatste regering in. Start zo nodig het script opnieuw om ook de laatste regering af te sluiten.")
else:
    pass
