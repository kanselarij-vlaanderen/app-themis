#!/usr/bin/env python3

from string import Template
import datetime
import os
import sys
import urllib.error
from uuid import uuid4 as generate_uuid

from pytz import timezone
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

APP_FOLDER = "/data/app/"
MIGRATIONS_FOLDER = APP_FOLDER + "config/migrations/"
FILES_FOLDER = APP_FOLDER + "data/files/"
CONSTRUCT_QUERY_FILE = APP_FOLDER + "scripts/generate-dataset/queries/construct_samenstelling_vr_dataset.sparql"
GRAPH = "http://mu.semte.ch/graphs/public"
MINISTER_DATASET_TYPE = "http://themis.vlaanderen.be/id/concept/dataset-type/43c644d3-2171-4892-8dd7-3fd5eec15d09"
SPARQL_ENDPOINT = os.environ.get("SPARQL_ENDPOINT", "http://triplestore:8890/sparql")

BRUSSELS_TZ = timezone('Europe/Brussels')

PREVIOUS_DATASET_QUERY = Template("""
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT ?dataset
WHERE {
    GRAPH <$graph> {
        ?dataset a dcat:Dataset ;
            dct:type <$dataset_type> ;
            dct:issued ?issued .
    }
}
ORDER BY DESC(?issued)
LIMIT 1
""").substitute(graph=GRAPH, dataset_type=MINISTER_DATASET_TYPE)

db = Graph(SPARQLStore(query_endpoint=SPARQL_ENDPOINT))

# Find the dataset that the new one will be a revision of
previous_dataset_uri = None
try:
    for row in db.query(PREVIOUS_DATASET_QUERY):  # only iterates max once (LIMIT 1)
        previous_dataset_uri = str(row.dataset)
except urllib.error.URLError as e:
    sys.exit(("Failed to query {} ({}).\n"
              "Make sure the triplestore is up and running").format(SPARQL_ENDPOINT, e))
if previous_dataset_uri:
    print("Previous dataset: {}".format(previous_dataset_uri))
else:
    print("No previous minister dataset found. The new dataset won't have a prov:wasRevisionOf link.")

# Generate the TTL dataset dump
with open(CONSTRUCT_QUERY_FILE) as f:
    construct_query = f.read()
dump_graph = db.query(construct_query).graph
if not dump_graph or len(dump_graph) == 0:
    sys.exit("The CONSTRUCT query returned an empty result. Not generating a dataset.")

share_file_uuid = str(generate_uuid())
file_name = share_file_uuid + ".ttl"
dump_file_path = FILES_FOLDER + file_name
dump_graph.serialize(destination=dump_file_path, format='turtle')
file_bytesize = os.stat(dump_file_path).st_size
print("Wrote dataset dump to {} ({} triples, {} bytes)".format(
    os.path.relpath(dump_file_path, APP_FOLDER), len(dump_graph), file_bytesize))

# Generate the migration with dataset/distribution/file metadata
with open("/templates/minister-new-dcat-dataset.ttl") as f:
    ttl_template = Template(f.read())

now = datetime.datetime.now(BRUSSELS_TZ)
ttl_result = ttl_template.substitute(
    DATASET_UUID=generate_uuid(),
    CREATION_DATE=now.isoformat(),
    DISTRIBUTION_UUID=generate_uuid(),
    FILE_UUID=generate_uuid(),
    SHARE_FILE_NAME=file_name,
    SHARE_FILE_UUID=share_file_uuid,
    FILE_BYTESIZE=file_bytesize,
    PREVIOUS_DATASET=previous_dataset_uri,
)
if not previous_dataset_uri:
    ttl_result = "\n".join(line for line in ttl_result.splitlines()
                           if "prov:wasRevisionOf" not in line) + "\n"

target_ttl_filename = MIGRATIONS_FOLDER + "{}-minister-new-dcat-dataset.ttl".format(now.strftime("%Y%m%d%H%M%S"))
with open(target_ttl_filename, "w") as f:
    f.write(ttl_result)

target_graph_filename = target_ttl_filename.replace(".ttl", ".graph")
with open(target_graph_filename, "w") as f:
    f.write(GRAPH)

print("Wrote migration to {}".format(os.path.relpath(target_ttl_filename, APP_FOLDER)))
print("Don't forget to stage the dump file in git (contents of ./data/files are gitignored by default).")
