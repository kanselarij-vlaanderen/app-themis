from pytz import timezone
import sys
import os
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

### CONSTANTS ###

BRUSSELS_TZ = timezone('Europe/Brussels')

VLAAMSE_REGERING = "http://themis.vlaanderen.be/id/bestuursorgaan/7f2c82aa-75ac-40f8-a6c3-9fe539163025"

MP = "http://themis.vlaanderen.be/id/bestuursfunctie/5fed907ce6670526694a03de"
VICE_MP = "http://themis.vlaanderen.be/id/bestuursfunctie/5fed907ce6670526694a03df"
MINISTER = "http://themis.vlaanderen.be/id/bestuursfunctie/5fed907ce6670526694a03e0"
# These don't exist on themis but are needed for kaleidos. remove from themis migrations after copy
SECRETARIS = "http://themis.vlaanderen.be/id/bestuursfunctie/9d5ebfb9-3829-4b1f-a2a8-15033f7e2097"
WAARNEMEND_SECRETARIS = "http://themis.vlaanderen.be/id/bestuursfunctie/cfa6ed74-bb6f-4d4c-b905-9a205be135d7"

BESTUURSFUNCTIES = [
    MP,
    VICE_MP,
    MINISTER,
    SECRETARIS,
    WAARNEMEND_SECRETARIS
]
### CONFIG ###

GRAPH = "http://mu.semte.ch/graphs/public"

APP_FOLDER = "/data/app/"
LATEST_DATASET_QUERY_FILE = APP_FOLDER + "scripts/generate-mandatees/queries/latest-govt-dataset.sparql"
SPARQL_ENDPOINT = os.environ.get("SPARQL_ENDPOINT", "http://triplestore:8890/sparql")

def find_latest_dataset_dump():
    with open(LATEST_DATASET_QUERY_FILE) as f:
        query = f.read()
    db = Graph(SPARQLStore(query_endpoint=SPARQL_ENDPOINT))
    try:
        for row in db.query(query):  # results are ordered by creation date, we only need the first
            print("Latest government dataset according to Virtuoso: {} ({})".format(row.dataset, row.creation_date))
            return str(row.file_path)
    except (OSError, ValueError) as e:
        # rdflib's SPARQLConnector re-raises connection errors as ValueError
        e = e.__context__ or e
        sys.exit(("Failed to query Virtuoso at {} ({}).\n"
            "Make sure the triplestore container is running, "
            "or provide the path to the dataset dump file explicitly:\n"
            "mu script project-scripts generate-mandatees data/files/<uuid>.ttl").format(SPARQL_ENDPOINT, e))
    sys.exit("No government dataset found in Virtuoso. Provide the path to the dataset dump file explicitly.")

if len(sys.argv) == 1:
    MANDATEE_TTL_DATASET_FILE = os.path.normpath(os.path.join(APP_FOLDER, find_latest_dataset_dump()))
elif len(sys.argv) == 2:
    MANDATEE_TTL_DATASET_FILE = os.path.join(APP_FOLDER, sys.argv[1])
else:
    print("mu script project-scripts generate-mandatees [dataset-dump]")
    print("  dataset-dump: optional path to the government dataset ttl dump file (relative to project root).")
    print("                When omitted, the latest dump is looked up in Virtuoso (queries/latest-govt-dataset.sparql).")
    sys.exit()

if not os.path.isfile(MANDATEE_TTL_DATASET_FILE):
    raise Exception(MANDATEE_TTL_DATASET_FILE + " isn't a valid path to the latest government dataset ttl dump file")

MIGRATIONS_FOLDER = "/data/app/config/migrations/"

REGERINGSSAMENSTELLING_BASE_URI = "http://themis.vlaanderen.be/id/bestuursorgaan/"
LEGISLATUUR_BASE_URI = "http://themis.vlaanderen.be/id/bestuursorgaan/"
MANDAAT_BASE_URI = "http://themis.vlaanderen.be/id/mandaat/"
MANDATEE_BASE_URI = "http://themis.vlaanderen.be/id/mandataris/"
INVALIDATION_BASE_URI = "http://themis.vlaanderen.be/id/opheffing/"
GENERATION_BASE_URI = "http://themis.vlaanderen.be/id/creatie/"

