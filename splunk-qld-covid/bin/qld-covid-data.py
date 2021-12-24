from datetime import datetime
import json
import os
import sys
import time

import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

try:
    import requests
    from bs4 import BeautifulSoup
    from bs4.element import NavigableString, Tag
    from dateutil.tz import gettz as ZoneInfo
except ImportError as error_message:
    print(f"Failed to import library, {error_message}", file=sys.stderr)
    sys.exit(1)

URL = "https://www.qld.gov.au/health/conditions/health-alerts/coronavirus-covid-19/current-status/contact-tracing"


response = requests.get(URL)
response.raise_for_status()

soup = BeautifulSoup(response.content,features="lxml")

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
        print(f"Failed to parse '{date_string}' - {value_error}", file=sys.stderr)
        return False
    return datevar

def generate_suburb_hash(suburb_object: dict):
    """generates a value based on the input data"""
    lga = suburb_object.get('lgas','NA')
    suburb_str = suburb_object.get('suburb', "unknown_suburb")
    location = suburb_object.get('location','unknown_location')
    hashval = f"{lga}-{suburb_object['date']}-{suburb_str}-{location}"
    return hashval

tables = soup.find_all('table')

logged = 0

timestamp = int(time.time())

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
                            this_suburb["_time"] = timestamp
                            logged += 1
                            print(json.dumps(this_suburb, ensure_ascii=False))


print(f"Sent {logged} entries", file=sys.stderr)
