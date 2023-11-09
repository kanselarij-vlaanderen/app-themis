from pytz import timezone

### CONSTANTS ###

BRUSSELS_TZ = timezone('Europe/Brussels')

VLAAMSE_REGERING = "http://themis.vlaanderen.be/id/bestuursorgaan/7f2c82aa-75ac-40f8-a6c3-9fe539163025"

MP = "https://themis.vlaanderen.be/id/bestuursfunctie/5fed907ce6670526694a03de"
VICE_MP = "http://themis.vlaanderen.be/id/bestuursfunctie/5fed907ce6670526694a03df"
MINISTER = "http://themis.vlaanderen.be/id/bestuursfunctie/5fed907ce6670526694a03e0"

BESTUURSFUNCTIES = [
    MP,
    VICE_MP,
    MINISTER
]
### CONFIG ###

GRAPH = "http://mu.semte.ch/graphs/public"
# This file isn't a static parameter. It changes each time a new dump is generated.
# TODO: make the filename an argument of the script. Which filename to use can be determined by
# querying the prod DB
MANDATEE_TTL_DATASET_FILE = "/data/app/data/files/73089dee-7f76-42ba-9b06-556ff2bc5816.ttl"
MIGRATIONS_FOLDER = "/data/app/config/migrations/"

REGERINGSSAMENSTELLING_BASE_URI = "http://themis.vlaanderen.be/id/bestuursorgaan/"
LEGISLATUUR_BASE_URI = "http://themis.vlaanderen.be/id/bestuursorgaan/"
MANDAAT_BASE_URI = "http://themis.vlaanderen.be/id/mandaat/"
INVALIDATION_BASE_URI = "http://themis.vlaanderen.be/id/opheffing/"
GENERATION_BASE_URI = "http://themis.vlaanderen.be/id/creatie/"

