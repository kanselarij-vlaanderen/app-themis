from pytz import timezone
import sys
import os

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

if len(sys.argv) != 2:
    print("Please provide a path to the latest government dataset dump file")
    print("mu script project-scripts generate-mandatees dataset-dump")
    print("  dataset-dump: path to government dataset ttl dump file (relative to project root)")
    sys.exit()

MANDATEE_TTL_DATASET_FILE = os.path.join("/data/app/", sys.argv[1])
if not os.path.isfile(MANDATEE_TTL_DATASET_FILE):
    raise Exception(MANDATEE_TTL_DATASET_FILE + "isn't a valid path to the latest government dataset ttl dump file")

MIGRATIONS_FOLDER = "/data/app/config/migrations/"

REGERINGSSAMENSTELLING_BASE_URI = "http://themis.vlaanderen.be/id/bestuursorgaan/"
LEGISLATUUR_BASE_URI = "http://themis.vlaanderen.be/id/bestuursorgaan/"
MANDAAT_BASE_URI = "http://themis.vlaanderen.be/id/mandaat/"
INVALIDATION_BASE_URI = "http://themis.vlaanderen.be/id/opheffing/"
GENERATION_BASE_URI = "http://themis.vlaanderen.be/id/creatie/"

