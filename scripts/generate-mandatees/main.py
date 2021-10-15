#!/usr/bin/env python3
from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
from uuid import uuid4 as generate_uuid
from rdflib import Graph, Namespace, Literal, URIRef
from prompt_toolkit.validation import Validator, ValidationError
from validation import DateValidator, NumberValidator
import datetime
from generate_mandatees import ask_about_mandatee
from generate_government_body import ask_about_end_regeringssamenstelling, ask_about_end_legislatuur

MIGRATIONS_FOLDER = "/data/app/config/migrations/"

THEMIS_GOV_DATASET_MODEL_DOC = "https://themis-test.vlaanderen.be/docs/catalogs"
THEMIS_GOV_DATASET_MODEL_DOC_SRC = "https://github.com/kanselarij-vlaanderen/frontend-themis/blob/8b288d6af5f67f2ade1ed69f4eeb630d40929105/app/templates/docs/catalogs.hbs#L255"


questions = [
    {
        'type': 'list',
        'name': 'flowType',
        'message': 'Wat wil u doen?',
        'choices': [
            {
                'name': 'Een regeringssamenstelling afsluiten',
            },
            {
                'name': 'Een legislatuur afsluiten',
            },
            {
                'name': 'Een nieuwe regeringssamenstelling (binnen een lopende legislatuur) starten',
            },
            {
                'name': 'Een nieuwe legislatuur starten',
            }
        ]
    }
]

print("\n\nWelkom. Om onderstaande vragen goed te kunnen interpreteren," + \
    " \ is het belangrijk om de terminologie omtrent regeringen en mandaten te begrijpen." + \
    " \nRaadpleeg bij twijfel {} (sources op {})\n".format(THEMIS_GOV_DATASET_MODEL_DOC, THEMIS_GOV_DATASET_MODEL_DOC_SRC))
answers = prompt(questions)
flow_type = answers["flowType"]

if flow_type == "Een regeringssamenstelling afsluiten":
    query_string = ask_about_end_regeringssamenstelling()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = MIGRATIONS_FOLDER + "{}-end_regeringssamenstelling.sparql".format(timestamp)
    with open(filename, "w") as f:
        f.write(query_string)
elif flow_type == "Een legislatuur afsluiten":
    query_string = ask_about_end_legislatuur()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = MIGRATIONS_FOLDER + "{}-end-legislatuur.sparql".format(timestamp)
    with open(filename, "w") as f:
        f.write(query_string)
    print("Het beëindigen van een legislatuur houdt normaal gezien ook het beëindigen van de laatste regeringssamenstelling in." + \
    " Start zo nodig het script opnieuw om ook de laatste regeringssamenstelling af te sluiten.")
else:
    pass
