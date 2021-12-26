#!/usr/bin/env python3

import json
import os
import sys
#import time
import csv

import lxml.etree


IGNORE_TAGS = [
    "member",
]
IGNORE_KEYS = [
    "admin_level",
    "place",
    "source",
    "type",
    "boundary",
]

DIRNAME = "psma-admin-bdy-2020-08"
FILES_TO_PARSE = [
    "qld_2020-08_import_merged.osm",
    "wa_2020-08_import_merged.osm",
    "vic_2020-08_import_merged.osm",
    "nt_2020-08_import_merged.osm",
    "sa_2020-08.osm",
    "act_2020-08.osm",
    "tas_2020-08.osm",
]

# LXML things - https://stackoverflow.com/questions/50456954/parsing-osm-xml-data-with-python-with-specific-sub-tags#50457156
def parse_tag(child_object):
    """ parses a child tag """
    tagdata = {}
    for child in child_object.getparent().iterchildren():
        if child.tag not in IGNORE_TAGS:
            if child.get("k") not in IGNORE_KEYS:
                key = child.get("k").replace("ref:psma:", "").replace("psma:", "")
                # print(f"{key} - {child.get('v')}")
                tagdata[key] = child.get("v")
    # print(json.dumps(tagdata, ensure_ascii=False))
    return tagdata

fulldata = []
for filename in FILES_TO_PARSE:

    if not os.path.exists(f"{DIRNAME}/{filename}"):
        print(f"Failed to find {DIRNAME}/{filename}, skipping", file=sys.stderr)
        continue
    print(f"Parsing {filename}", file=sys.stderr)
    tree = lxml.etree.parse(f"{DIRNAME}/{filename}")
    # grab the administrative boundaries
    for tag in tree.findall("//relation//tag[@k='ref:psma:lga_pid']"):
        tagval = parse_tag(tag)
        if tagval not in fulldata:
            fulldata.append(tagval)
    for tag in tree.findall("//relation//tag[@k='psma:lga_pid']"):
        tagval = parse_tag(tag)
        if tagval not in fulldata:
            fulldata.append(tagval)
    print(f"Current count: {len(fulldata)}")

print(f"Found {len(fulldata)} LGAs")

CSV_FIELDS = [
    "lga_pid",
    "lga_visible",
    "short_name",
    "name"
]

# adding in the ACT
print("Manually adding ACT")
data = {
    "lga_pid" : "ACT1",
    "name" : "Territory and Municipal Services Directorate",
    "short_name" : "ACT",
}
fulldata.append(data)


filename = 'qld_covid_data/lookups/qldcovid_lga.csv'
print(f"Writing {filename}")
with open(filename, 'w', newline='', encoding="utf8") as csvfile:
    writer = csv.DictWriter(csvfile,
                        fieldnames=CSV_FIELDS,
                        dialect="unix",
    )

    writer.writeheader()
    for data in fulldata:
        data["lga_visible"] = f"{data['lga_pid']} - {data['name']}"
        writer.writerow(data)
