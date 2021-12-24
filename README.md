# splunk-qld-covid

## Splunk-side things

I've turned this into an app - the file's at `splunk-qld-covid.spl`.

### Macros


| Macro name | Default Value | Description |
| --- | --- | --- |
| `covid_sourcedata` | `sourcetype="covid:qldhealth"` | Where you sent the data through the ingester |
| `covid_lgadata` | `sourcetype="qldcovid:lgadata"` | LGA Data from osmfinder.py |


### Enabling the input

Look for the script called `qld-covid-data.py` - there's a default cron schedule of every hour.

## Usage of the standalone script

### Create a config.py:

```
hechostname = "example.com"
hectoken = "<my_fancy_token>"
```

You can also add `hecindex` and `hecsourcetype` elements to configure that, else it'll use the default index and `_json` as the sourcetype.

### Running the thing

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

python3 qld_covid_data.py
```

# Notes about LGA Data 

## What are these LGA IDs?

After much muttering and searching I found [this boundary on OpenStreetMap](https://www.openstreetmap.org/relation/5656285#map=9/-24.8752/152.4408)

Which led me to this: https://wiki.openstreetmap.org/wiki/Import/Catalogue/PSMA_Admin_Boundaries

In this document: https://geoscape.com.au/wp-content/uploads/2021/08/Local-Government-Areas-Product-Guide-v1.0.pdf

![lga pid screenshot](assets/lga_pid_screenshot.png)

## Extracting the data
I extracted it from the data in https://github.com/FrakGart/psma-admin-bdy-2020-08 using `osmfinder.py`.

Grabbing the source data:

```
git clone --depth 1 https://github.com/FrakGart/psma-admin-bdy-2020-08 
```

Some other files need decompression:

```
xz -d psma-admin-bdy-2020-08/act_2020-08.osm.xz
xz -d psma-admin-bdy-2020-08/nsw_2020-08.osm.xz
xz -d psma-admin-bdy-2020-08/sa_2020-08.osm.xz
xz -d psma-admin-bdy-2020-08/tas_2020-08.osm.xz
```

There's no "level 6" admin boundary defined for ACT... in this data anyway.

## Importing the LGA data

Run `osmfinder.py` once - it'll use the sourcetype `qldcovid:lgadata` - if you want to change that, it's set at the top of the script.

(It's also a lookup csv file in the app)

# Finally 

Eat some cake 🍰

# Credits:

 - App icon by [NawIcon](https://thenounproject.com/nawiconstudio/)  from The Noun Project - https://thenounproject.com/icon/virus-3364075/
 - [Requests](https://docs.python-requests.org/en/master/index.html) is HTTP for Humans. 
 - [BeautifulSoup4](http://beautiful-soup-4.readthedocs.io) for parsing HTML.
 - [dateutil](https://pypi.org/project/python-dateutil/) for timezones.
 - [lxml](https://pypi.org/project/python-dateutil/) else we'd never get any XML done.
 - [openstreetmap](http://openstreetmap.org) because they had done the hard yards on the LGA info.
 