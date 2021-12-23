#!/bin/bash

CURRDIR="$(pwd)"
cd "$(dirname "$0")" || exit 1

#shellcheck disable=SC1091
source venv/bin/activate

python3 qld_covid_data.py
cd "${CURRDIR}" || exit 1