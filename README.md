# splunk-qld-covid

## Splunk-side things

I've put my example dashboard and the saved search that powers it in the `splunk_*` folders.

## Usage

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

Eat some cake 🍰