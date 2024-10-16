#!/usr/bin/env python3
import os
import datetime
from PyInquirer import prompt, print_json
from prompt_toolkit.validation import Validator, ValidationError
from config import BRUSSELS_TZ, MIGRATIONS_FOLDER
from mandatees import mandatee_generation_loop
from duplicate_mandatee import duplicate_mandatees
from regeringssamenstelling import ask_about_end_regeringssamenstelling, \
    ask_about_start_regeringssamenstelling, \
    ask_about_current_regeringssamenstelling
from legislatuur import ask_about_end_legislatuur, ask_about_start_legislatuur

THEMIS_GOV_DATASET_MODEL_DOC = "https://themis-test.vlaanderen.be/docs/catalogs"
THEMIS_GOV_DATASET_MODEL_DOC_SRC = "https://github.com/kanselarij-vlaanderen/frontend-themis/blob/8b288d6af5f67f2ade1ed69f4eeb630d40929105/app/templates/docs/catalogs.hbs#L255"

END_SAMENSTELLING = 'Een regeringssamenstelling afsluiten'
END_LEGISLATUUR = 'Een legislatuur afsluiten'
START_SAMENSTELLING = 'Een nieuwe regeringssamenstelling (binnen een lopende legislatuur) starten'
START_LEGISLATUUR = 'Een nieuwe legislatuur starten'
UPDATE_MANDATEES = 'Veranderingen in mandatarissen binnen een bestaande regeringssamenstelling'
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

now = datetime.datetime.now(BRUSSELS_TZ)
if flow_type == END_SAMENSTELLING:
    query_string = ask_about_end_regeringssamenstelling()
    filename = MIGRATIONS_FOLDER + "{}-end_regeringssamenstelling.sparql".format(now.strftime("%Y%m%d%H%M%S"))
    with open(filename, "w") as f:
        f.write(query_string)
elif flow_type == END_LEGISLATUUR:
    query_string = ask_about_end_legislatuur()
    filename = MIGRATIONS_FOLDER + "{}-end-legislatuur.sparql".format(now.strftime("%Y%m%d%H%M%S"))
    with open(filename, "w") as f:
        f.write(query_string)
    print("Het beëindigen van een legislatuur houdt normaal gezien ook het beëindigen van de laatste regeringssamenstelling in." + \
    " Start zo nodig het script opnieuw om ook de laatste regeringssamenstelling af te sluiten.")
elif flow_type == START_SAMENSTELLING:
    query_string = ask_about_start_regeringssamenstelling()
    filename = MIGRATIONS_FOLDER + "{}-start-samenstelling.sparql".format(now.strftime("%Y%m%d%H%M%S"))
    with open(filename, "w") as f:
        f.write(query_string)
    print("Het starten van een regeringssamenstelling houdt normaal gezien ook het aanmaken van nieuwe mandataris-entiteiten in." + \
    " Start zo nodig het script opnieuw om mandatarissen aan te maken.")
elif flow_type == START_LEGISLATUUR:
    query_string = ask_about_start_legislatuur()
    filename = MIGRATIONS_FOLDER + "{}-start-legislatuur.sparql".format(now.strftime("%Y%m%d%H%M%S"))
    with open(filename, "w") as f:
        f.write(query_string)
    print("Een migratie voor het aanmaken van een nieuwe legislatuur werd gegenereerd. " + \
    "Ook de mandaten voor een nieuwe legislatuur werden toegevoegd.")
    print("Het starten van een legislatuur houdt normaal gezien ook het aanmaken van een nieuwe regeringssamenstelling in." + \
    " Start zo nodig het script opnieuw om een regeringssamenstelling aan te maken.")
elif flow_type == UPDATE_MANDATEES:
    start_date_default = BRUSSELS_TZ.localize(datetime.datetime(now.year, now.month, now.day))
    samenstelling = ask_about_current_regeringssamenstelling()
    g = duplicate_mandatees(samenstelling, start_date_default)
    g = g + mandatee_generation_loop(samenstelling)
    filename_without_ext = MIGRATIONS_FOLDER + "{}-new-minister-data".format(now.strftime("%Y%m%d%H%M%S"))
    filename = '{}.ttl'.format(filename_without_ext)
    g.serialize(destination=filename, format='turtle')
    # TODO: add graph file
elif flow_type == GEN_MANDATEES:
    samenstelling = ask_about_current_regeringssamenstelling()
    g = mandatee_generation_loop(samenstelling)
    filename_without_ext = MIGRATIONS_FOLDER + "{}-new-minister-data".format(now.strftime("%Y%m%d%H%M%S"))
    filename = '{}.ttl'.format(filename_without_ext)
    g.serialize(destination=filename, format='turtle')
    # TODO: add graph file
else:
    filename = None

if filename:
    print("Wrote migration file to {}".format(os.path.relpath(filename, "/data/app")))
    if os.path.splitext(filename)[1] == '.ttl':
        print("Verify if you want to add a .graph-file manually")
