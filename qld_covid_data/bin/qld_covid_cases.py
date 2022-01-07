"""parses the Queensland Health COVID-19 cases data and returns each event as a JSON blob on a line"""


from inspect import currentframe, getframeinfo

# from datetime import datetime
import json
from json.decoder import JSONDecodeError
import os
import sys
import time

# allow Splunk's python to include libs from the app lib dir
include_dir = os.path.join(os.path.dirname(__file__), "..", "lib")
if os.path.exists(include_dir):
    sys.path.insert(0, include_dir)

try:
    import requests
except ImportError as error_message:
    print(f"Failed to import library, {error_message}", file=sys.stderr)
    sys.exit(1)

URL = "https://www.data.qld.gov.au/datastore/dump/1dbae506-d73c-4c19-b727-e8654b8be95a?format=json"

try:
    response = requests.get(url=URL)
    response.raise_for_status()
except requests.exceptions.ConnectTimeout as connection_error:
    print("ConnectTimeout to '{URL}', bailing: {connection_error}", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.ConnectionError as connection_error:
    print("ConnectionError to '{URL}', bailing: {connection_error}", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.RequestException as connection_error:
    print("RequestException to '{URL}', bailing: {connection_error}", file=sys.stderr)
    sys.exit(1)
except Exception as connection_error: # pylint: disable=broad-except
    print("Exception pulling '{URL}', bailing: {connection_error}", file=sys.stderr)
    sys.exit(1)


try:
    data = response.json()
except JSONDecodeError as decode_error:
    print(f"JSONDecodeError parsing page content, bailing: {decode_error}", file=sys.stderr)
    sys.exit(1)
# with open("cached-cases.json", encoding="utf8") as loader:
#     data = json.load(loader)

LOGGED = 0
timestamp = time.time()

# first, parse the fields data
fields = []

for field in data.get("fields"):
    field_id = field.get("id").lstrip("_").lower()
    fields.append(field_id)

for source_record in data.get("records"):
    record = {
        "_time" : timestamp
    }
    for index, element in enumerate(source_record):
        record[fields[index]] = element
    print(json.dumps(record, ensure_ascii=False))
    LOGGED += 1


# grab the script filename
current_frame = currentframe()
if current_frame:
    frameinfo = getframeinfo(current_frame)
    print(f"Returned {LOGGED} results from {frameinfo.filename}", file=sys.stderr)
else:
    print(f"Returned {LOGGED} results",file=sys.stderr)
