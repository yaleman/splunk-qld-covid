# Splunking Queensland Health COVID Data

## Splunk-side things

I've turned this into an app - the file's at `qld_covid_data.spl`.

### Macros


| Macro name | Default Value | Description |
| --- | --- | --- |
| `qldcovid_sourcedata` | `sourcetype="qldcovid:contacts"` | Where you sent the data through the ingester |
| `qldcovid_lgadata` | `| inputlookup qldcovid_lga` | LGA Data from the lookup |

### Inputs

| Name | Script Filename | Description | Default Schedule | Official Update Frequency | 
| Contact Data | `qld_covid_contacts.py` | Queensland Health Contact tracing data from [here](https://www.qld.gov.au/health/conditions/health-alerts/coronavirus-covid-19/current-status/contact-tracing)  | `12 * * * *` (every hour, at 12 minutes past the hour) | Irregular - whenever they post them |
| Case Data | `qld_covid_cases.py` | Queensland Health COVID-19 case data from [here](https://www.data.qld.gov.au/dataset/queensland-covid-19-case-line-list-location-source-of-infection)  | `13 17 * * *` (5PM daily, at 13 minutes past the hour) | Weekly |


# Notes about LGA Data 

## What are these LGA IDs?

After much muttering and searching I found [this boundary on OpenStreetMap](https://www.openstreetmap.org/relation/5656285#map=9/-24.8752/152.4408)

Which led me to this: https://wiki.openstreetmap.org/wiki/Import/Catalogue/PSMA_Admin_Boundaries

In this document: https://geoscape.com.au/wp-content/uploads/2021/08/Local-Government-Areas-Product-Guide-v1.0.pdf

![lga pid screenshot](assets/lga_pid_screenshot.png)

The file that made me realise I wasn't looking for some truly random thing was here: https://www.nhvr.gov.au/files/201904-1033-local-council-and-road-authority-contact-numbers.pdf

![nhvr screenshot](assets/nhvr_screenshot.png)

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

## Generating the LGA data

Run `osmfinder.py` - it'll update the lookup csv file in the app.

# Finally 

Eat some cake 🍰

# Version history

 - 0.0.1 - 0.0.2 : Initial Releases
 - 0.0.3 : Added case data

# Credits:

 - App icon by [NawIcon](https://thenounproject.com/nawiconstudio/)  from The Noun Project - https://thenounproject.com/icon/virus-3364075/
 - [Requests](https://docs.python-requests.org/en/master/index.html) is HTTP for Humans. 
 - [BeautifulSoup4](http://beautiful-soup-4.readthedocs.io) for parsing HTML.
 - [dateutil](https://pypi.org/project/python-dateutil/) for timezones.
 - [lxml](https://pypi.org/project/python-dateutil/) else we'd never get any XML done.
 - [openstreetmap](http://openstreetmap.org) because they had done the hard yards on the LGA info.
 

