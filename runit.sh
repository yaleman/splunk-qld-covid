#!/bin/bash

cd "$(dirname "$@")" || exit 1

#shellcheck disable=SC1091
source venv/bin/activate

python3 qld_covid_data.py
