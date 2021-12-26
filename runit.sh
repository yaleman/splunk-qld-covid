#!/bin/bash

CURRDIR="$(pwd)"
cd "$(dirname "$0")" || exit 1

if [ ! -d venv ]; then
    python3 -m venv venv || virtualenv venv
fi


#shellcheck disable=SC1091
source venv/bin/activate

python3 -m pip install --upgrade -r requirements.txt

python3 qld_covid_data/bin/qld_covid_contacts.py
cd "${CURRDIR}" || exit 1