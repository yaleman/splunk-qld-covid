#!/usr/bin/env bash

find "./splunk-qld-covid" -name '*.pyc' -delete

# find "./splunk-qld-covid" -name '.*'

find "./splunk-qld-covid" -type f -exec chmod 600 "{}" \;
find . -name '*.DS_Store' -delete

#echo "Ensuring splunklib is up to date"
#python3 -m pip install --upgrade -t splunk-qld-covid/lib/ splunk-sdk

echo "Removing bs4 testing file because it has biased language."
rm splunk-qld-covid/lib/bs4/testing.py

COPYFILE_DISABLE=1 tar czvf splunk-qld-covid.spl splunk-qld-covid/
echo "Created splunk-qld-covid.spl"