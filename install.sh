#!/bin/bash

if [ ! -d "./venv/" ]; then
    echo "Creating virtualenv"
    python3 -m venv venv || virtualenv venv || exit 1
fi

source venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade -r requirements.txt
