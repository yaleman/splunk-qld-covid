"""parses the Queensland Health COVID-19 Contact Tracing page and returns each event as a JSON blob on a line"""


from inspect import currentframe, getframeinfo

from datetime import datetime
import json
import os
import sys
import time

import urllib.parse

# allow Splunk's python to include libs from the app lib dir
include_dir = os.path.join(os.path.dirname(__file__), "..", "lib")
if os.path.exists(include_dir):
    sys.path.insert(0, include_dir)

try:
    import requests
    from bs4 import BeautifulSoup
    from bs4.element import NavigableString, Tag
    from dateutil.tz import gettz as ZoneInfo
except ImportError as error_message:
    print(f"Failed to import library, {error_message}", file=sys.stderr)
    sys.exit(1)

URL = "https://www.qld.gov.au/health/conditions/health-alerts/coronavirus-covid-19/current-status/contact-tracing"


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
    lga = "".join(suburb_object.get('lgas',['NA']))
    suburb_str = suburb_object.get('suburb', "unknown_suburb")
    location = suburb_object.get('location','unknown_location')
    hashval = f"{lga}-{suburb_object['date']}-{suburb_str}-{location}"
    return hashval


try:
    response = requests.get(URL)
    response.raise_for_status()
except requests.exceptions.ConnectionError as connection_error:
    print("ConnectionError to '{URL}', bailing: {connection_error}", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.ConnectTimeout as connection_error:
    print("ConnectTimeout to '{URL}', bailing: {connection_error}", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.RequestException as connection_error:
    print("RequestException to '{URL}', bailing: {connection_error}", file=sys.stderr)
    sys.exit(1)
except Exception as connection_error:
    print("Exception pulling '{URL}', bailing: {connection_error}", file=sys.stderr)
    sys.exit(1)

try:
    soup = BeautifulSoup(response.content,features="lxml")
except Exception as souperror:
    print(f"Exception parsing page content, bailing: {souperror}", file=sys.stderr)
    sys.exit(1)

logged = 0
timestamp = time.time()

tables = soup.find_all('table')
if not tables:
    print("Found no tables while parsing page, quitting.", file=sys.stderr)
    sys.exit(1)

def clean_value(value_str: str, key_name: str):
    """ returns a cleaned value """
    value = urllib.parse.unquote_plus(value_str)

    value = value.replace('\r', " ")
    value = value.replace('\n', " ")
    while "  " in value:
        value = value.replace("  ", " ")
    if key_name == "lgas":
        value = value.split(",")
    return value


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
                                    # clean up the value
                                    this_suburb[keyname] = clean_value(tr.attrs[key], keyname)

                            if "suburb" not in this_suburb or  this_suburb.get("suburb", "").strip() == "":
                                this_suburb["suburb"] = "Unknown"

                            if "lgas" not in this_suburb:
                                if suburb.lower().endswith(" act"):
                                    this_suburb["lgas"] = ["ACT1"]
                                else:
                                    this_suburb["lgas"] = ["Unspecified"]

                            suburb_hash = generate_suburb_hash(this_suburb)
                            this_suburb["hash"] = suburb_hash
                            this_suburb["_time"] = timestamp
                            logged += 1
                            print(json.dumps(this_suburb, ensure_ascii=False))


# grab the script filename
frameinfo = getframeinfo(currentframe())
print(f"Returned {logged} results from {frameinfo.filename}", file=sys.stderr)
