#!/usr/bin/env python3
# coding: utf-8
""" parses the Queensland Health Covid Contacts page and pushes to HEC """

from datetime import datetime
import time
import json

import urllib.parse
import sys

try:
    import requests
    from bs4 import BeautifulSoup
    from bs4.element import NavigableString, Tag
except ImportError as error_message:
    print("Failed to import library, run python3 -m pip install -r requirements.txt", file=sys.stderr)
    print(error_message, file=sys.stderr)
    sys.exit(1)
if sys.version_info.major == 3 and sys.version_info.minor==9:
    # disabling reportmissingimports because it only exists in 3.9.x
    from zoneinfo import ZoneInfo # pyright: reportMissingImports=false
else:
    try:
        from dateutil.tz import gettz as ZoneInfo
    except ImportError as error_message:
        print("Failed to import library, run python3 -m pip install -r requirements.txt", file=sys.stderr)
        print(error_message, file=sys.stderr)
        sys.exit(1)

try:
    from . import config
    if not hasattr(config,"hechostname"):
        print("Failed to find hechostname in config, please configure", file=sys.stderr)
        sys.exit(1)
    if not hasattr(config,"hectoken"):
        print("Failed to find hectoken in config, please configure", file=sys.stderr)
        sys.exit(1)
except ImportError as import_error_message:
    print(f"Failed to import config, quitting: {import_error_message}", file=sys.stderr)
    sys.exit(1)

URL = "https://www.qld.gov.au/health/conditions/health-alerts/coronavirus-covid-19/current-status/contact-tracing"

response = requests.get(URL)
response.raise_for_status()

soup = BeautifulSoup(response.content,features="lxml")

# with open("cached.html", encoding="utf-8") as filehandle:
#     soup = BeautifulSoup(filehandle.read(),features="lxml")

def parse_date(date_string: str):
    """parse the input date string,
    looks like %Y-%m-%dT%H:%M
    """
    if date_string.endswith('T00'):
        date_string = f"{date_string}:00"
    try:
        datevar = datetime.strptime(f"{date_string}:00",
                                "%Y-%m-%dT%H:%M:%S")
        datevar = datevar.replace(tzinfo=ZoneInfo("Australia/Brisbane"))
    except ValueError as value_error:
        print(f"Failed to parse '{date_string}' - {value_error}")
        return False
#     print(dir(datevar))
    return datevar

def generate_suburb_hash(suburb_object: dict):
    """generates a value based on the input data"""
    lga = suburb_object.get('lgas','NA')
    suburb_str = suburb_object.get('suburb', "unknown_suburb")
    location = suburb_object.get('location','unknown_location')
    hashval = f"{lga}-{suburb_object['date']}-{suburb_str}-{location}"
    return hashval

def send_data(entry:dict):
    """sends an event"""

    headers = {
        "Authorization" : f"Splunk {config.hectoken}",
    }
    payload = {
        "event" : json.dumps(entry, ensure_ascii=False),
    }

    if hasattr(config, "hecindex"):
        payload["index"] = config.hecindex
    if hasattr(config, "hecsourcetype"):
        payload["sourcetype"] = config.hecsourcetype
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

tables = soup.find_all('table')

fulldata = []

for table in tables:
    if not isinstance(table, NavigableString):
        for child in table.children:
            if not isinstance(child, NavigableString):
                if child.name=='tbody':
                    trs = child.children
                    for tr in trs:
                        if isinstance(tr, Tag):
                            for key in tr.attrs:
                                if key != 'class':
                                    tr[key]  = tr.get(key).replace('%20',' ')
                            suburb = urllib.parse.unquote_plus(tr.get("data-suburb","Unlisted"))
                            this_suburb = {}
                            for key in tr.attrs:
                                keyname = key.replace("data-", "")
                                if key == "class":
                                    pass
                                elif keyname in ("date", "added"):
                                    date = parse_date(tr.attrs.get(key))
                                    this_suburb[keyname] = date.isoformat()
                                else:
                                    value = urllib.parse.unquote_plus(tr.attrs[key])
                                    if keyname == "lgas":
                                        value = value.split(",")
                                    this_suburb[keyname] = value

                            suburb_hash = generate_suburb_hash(this_suburb)
                            this_suburb["hash"] = suburb_hash
                            fulldata.append(this_suburb)
                            send_data(this_suburb)
                            # print(json.dumps(this_suburb, indent=4, ensure_ascii=False))


print(f"Sent {len(fulldata)} entries")
