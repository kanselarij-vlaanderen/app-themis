#!/usr/bin/env python3
from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
from uuid import uuid4 as generate_uuid
from rdflib import Graph, Namespace, Literal, URIRef
from prompt_toolkit.validation import Validator, ValidationError
from validation import DateValidator, NumberValidator
import datetime
from mandatees import mandatee_generation_loop
from duplicate_mandatee import duplicate_mandatees
from regeringssamenstelling import ask_about_end_regeringssamenstelling, ask_about_start_regeringssamenstelling
from legislatuur import ask_about_end_legislatuur, ask_about_start_legislatuur

MIGRATIONS_FOLDER = "/data/app/config/migrations/"

THEMIS_GOV_DATASET_MODEL_DOC = "https://themis-test.vlaanderen.be/docs/catalogs"
THEMIS_GOV_DATASET_MODEL_DOC_SRC = "https://github.com/kanselarij-vlaanderen/frontend-themis/blob/8b288d6af5f67f2ade1ed69f4eeb630d40929105/app/templates/docs/catalogs.hbs#L255"

SAMENSTELLING = "http://themis.vlaanderen.be/id/bestuursorgaan/5fed907ee6670526694a0706" # TODO don't hardcode

END_SAMENSTELLING = 'Een regeringssamenstelling afsluiten'
END_LEGISLATUUR = 'Een legislatuur afsluiten'
START_SAMENSTELLING = 'Een nieuwe regeringssamenstelling (binnen een lopende legislatuur) starten'
START_LEGISLATUUR = 'Een nieuwe legislatuur starten'
UPDATE_MANDATEES = 'Mandatarissen binnen een bestaande regeringssamenstelling "updaten"'
GEN_MANDATEES = 'Mandatarissen voor een nieuwe regeringssamenstelling aanmaken'

questions = [
    {
        'type': 'list',
        'name': 'flowType',
        'message': 'Wat wil u doen?',
        'choices': [
            END_SAMENSTELLING,
            END_LEGISLATUUR,
            START_SAMENSTELLING,
            START_LEGISLATUUR,
            UPDATE_MANDATEES,
            GEN_MANDATEES
        ]
    }
]

print("\n\nWelkom. Om onderstaande vragen goed te kunnen interpreteren," + \
    "is het belangrijk om de terminologie omtrent regeringen en mandaten te begrijpen. \n" + \
    "Raadpleeg bij twijfel {} (sources op {})\n".format(THEMIS_GOV_DATASET_MODEL_DOC, THEMIS_GOV_DATASET_MODEL_DOC_SRC))
answers = prompt(questions)
flow_type = answers["flowType"]

if flow_type == END_SAMENSTELLING:
    query_string = ask_about_end_regeringssamenstelling()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = MIGRATIONS_FOLDER + "{}-end_regeringssamenstelling.sparql".format(timestamp)
    with open(filename, "w") as f:
        f.write(query_string)
elif flow_type == END_LEGISLATUUR:
    query_string = ask_about_end_legislatuur()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = MIGRATIONS_FOLDER + "{}-end-legislatuur.sparql".format(timestamp)
    with open(filename, "w") as f:
        f.write(query_string)
    print("Het beëindigen van een legislatuur houdt normaal gezien ook het beëindigen van de laatste regeringssamenstelling in." + \
    " Start zo nodig het script opnieuw om ook de laatste regeringssamenstelling af te sluiten.")
elif flow_type == START_SAMENSTELLING:
    query_string = ask_about_start_regeringssamenstelling()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = MIGRATIONS_FOLDER + "{}-start-samenstelling.sparql".format(timestamp)
    with open(filename, "w") as f:
        f.write(query_string)
    print("Het starten van een regeringssamenstelling houdt normaal gezien ook het aanmaken van nieuwe mandataris-entiteiten in." + \
    " Start zo nodig het script opnieuw om mandatarissen aan te maken.")
elif flow_type == START_LEGISLATUUR:
    query_string = ask_about_start_legislatuur()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = MIGRATIONS_FOLDER + "{}-start-legislatuur.sparql".format(timestamp)
    with open(filename, "w") as f:
        f.write(query_string)
    print("Een migratie voor het aanmaken van een nieuwe legislatuur werd gegenereerd. " + \
    "Ook de mandaten voor een nieuwe legislatuur werden toegevoegd.")
    print("Het starten van een legislatuur houdt normaal gezien ook het aanmaken van een nieuwe regeringssamenstelling in." + \
    " Start zo nodig het script opnieuw om een regeringssamenstelling aan te maken.")
elif flow_type == UPDATE_MANDATEES:
    now = datetime.datetime.now()
    start_date_default = datetime.datetime(now.year, now.month, now.day, tzinfo=datetime.timezone.utc)
    # TODO: ask about samenstelling uri and end_datetime
    g = duplicate_mandatees(SAMENSTELLING, start_date_default)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename_without_ext = MIGRATIONS_FOLDER + "{}-new-minister-data".format(timestamp)
    g.serialize(destination='{}.ttl'.format(filename_without_ext), format='turtle')
    # TODO: add graph file
elif flow_type == GEN_MANDATEES:
    # TODO: ask for samenstelling_uri once, then loop
    g = mandatee_generation_loop(SAMENSTELLING)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename_without_ext = MIGRATIONS_FOLDER + "{}-new-minister-data".format(timestamp)
    g.serialize(destination='{}.ttl'.format(filename_without_ext), format='turtle')
    # TODO: add graph file
else:
    pass
