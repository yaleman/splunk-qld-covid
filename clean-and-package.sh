#!/usr/bin/env bash


APPID="qld_covid_data"
APPDIR="./${APPID}/"


find "${APPDIR}" -name '*.pyc' -delete

# find "${APPDIR}" -name '.*'

find "${APPDIR}" -type f -exec chmod 600 "{}" \;
find . -name '*.DS_Store' -delete


if [ ! -d venv ]; then
    python3 -m venv venv || python3 -m virtualenv venv

fi
# shellcheck disable=SC1091
source venv/bin/activate

echo "Updating local packages for testing..."
python3 -m pip install --upgrade pip --quiet
python3 -m pip install --upgrade -r requirements-dev.txt --quiet

echo "Checking app config files"
find "${APPDIR}/" -name '*.conf' -exec ksconf check "{}" \;

# echo "Removing bs4 testing file because it has biased language."
# rm "${APPDIR}/lib/bs4/testing.py"
# rm "${APPDIR}/lib/bs4/diagnose.py"

echo "Setting permissions on lib dir"
find "${APPDIR}/lib" -type f -exec chmod 600 "{}" \;

rm "${APPID}.spl"

COPYFILE_DISABLE=1 tar czvf ${APPID}.spl \
    --exclude "*/lib/bs4/testing.py" \
    --exclude "*/lib/bs4/diagnose.py" \
    --exclude '*/__pycache__/*' \
    --exclude "*/lib/dateutil/zoneinfo/rebuild.py" \
    --exclude "*/lib/dateutil/zoneinfo/__init__.py" \
    "${APPDIR}"
echo "Created ${APPID}.spl"
