#!/usr/bin/env bash


APPID="qld_covid_data"
APPDIR="./${APPID}/"


find "${APPDIR}" -name '*.pyc' -delete

# find "${APPDIR}" -name '.*'

find "${APPDIR}" -type f -exec chmod 600 "{}" \;
find . -name '*.DS_Store' -delete

#echo "Ensuring splunklib is up to date"
#python3 -m pip install --upgrade -t "${APPDIR}/lib/" splunk-sdk

echo "Removing bs4 testing file because it has biased language."
rm "${APPDIR}/lib/bs4/testing.py"

echo "Setting permissions on lib dir"
find "${APPDIR}/lib" -type f -exec chmod 600 "{}" \;

COPYFILE_DISABLE=1 tar czvf ${APPID}.spl "${APPDIR}"
echo "Created ${APPID}.spl"