#!/usr/bin/env python3

from string import Template
import datetime
from uuid import uuid4 as generate_uuid
import glob
import os

from pytz import timezone

MIGRATIONS_FOLDER = "/data/app/config/migrations/"
FILES_FOLDER = "/data/app/data/files/"
GRAPH = "http://mu.semte.ch/graphs/public"

BRUSSELS_TZ = timezone('Europe/Brussels')

with open("/templates/minister-new-dcat-dataset.ttl") as f:
    ttl_template_string = f.read()

ttl_template = Template(ttl_template_string)

dataset_uuid = generate_uuid()
creation_date = datetime.datetime.now().isoformat()
distribution_uuid = generate_uuid()
file_uuid = generate_uuid()

ttl_files = glob.glob(FILES_FOLDER + "*.ttl")
last_ttl_file = max(ttl_files, key=os.path.getctime)
last_mod_time = datetime.datetime.fromtimestamp(os.stat(last_ttl_file).st_ctime).isoformat()
file_name = os.path.basename(last_ttl_file)
file_bytesize = os.stat(last_ttl_file).st_size

ttl_result = ttl_template.substitute(
    DATASET_UUID=dataset_uuid,
    CREATION_DATE=creation_date,
    DISTRIBUTION_UUID=distribution_uuid,
    FILE_UUID=file_uuid,
    SHARE_FILE_NAME=file_name,
    SHARE_FILE_UUID=file_name.replace(".ttl", ""),
    FILE_BYTESIZE=file_bytesize,
)

now = datetime.datetime.now(BRUSSELS_TZ)
target_ttl_filename = MIGRATIONS_FOLDER + "{}-minister-new-dcat-dataset.ttl".format(now.strftime("%Y%m%d%H%M%S"))
with open(target_ttl_filename, "w") as f:
    f.write(ttl_result)


target_graph_filename = target_ttl_filename.replace(".ttl", ".graph")
with open(target_graph_filename, "w") as f:
    f.write(GRAPH)
