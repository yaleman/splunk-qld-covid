#!/usr/bin/env python3

import json
import os
import sys
import time

import lxml.etree

import requests

try:
    import config
    if not hasattr(config,"hechostname"):
        print("Failed to find hechostname in config, please configure", file=sys.stderr)
        sys.exit(1)
    if not hasattr(config,"hectoken"):
        print("Failed to find hectoken in config, please configure", file=sys.stderr)
        sys.exit(1)
except ImportError as import_error_message:
    print(f"Failed to import config, quitting: {import_error_message}", file=sys.stderr)
    sys.exit(1)

SOURCETYPE = "qldcovid:lgadata"

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


def send_data(entry:dict, sourcetype=None):
    """sends an event"""

    headers = {
        "Authorization" : f"Splunk {config.hectoken}",
    }
    payload = {
        "event" : json.dumps(entry, ensure_ascii=False),
    }

    if hasattr(config, "hecindex"):
        payload["index"] = getattr(config, "hecindex")
    if hasattr(config, "hecsourcetype"):
        payload["sourcetype"] = getattr(config, "hecsourcetype")
    else:
        if sourcetype:
            payload["sourcetype"] = sourcetype
        else:
            payload["sourcetype"] = "_json"

    try:
        resp = requests.post(url=f"https://{config.hechostname}/services/collector/event", headers=headers, json=payload)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as req_error:
        print(resp.content, file=sys.stderr)
        print(req_error, file=sys.stderr)
        sys.exit(1)

    if not resp.json().get("text") == "Success":
        print("Sleeping and trying again")
        time.sleep(1)
        send_data(payload)


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

# for element in fulldata:
    # send_data(element, sourcetype=SOURCETYPE)
