#!/usr/bin/env python3
import requests
from mastodon import Mastodon
import os
import logging
from functools import reduce
import shapely
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger("BeachBot")
logging.basicConfig(level=logging.INFO)

server = os.environ.get("SERVER", "https://localhost")
token = os.environ.get("TOKEN", "insert coin")
max_len = 500

URL = "https://api.beachwatch.nsw.gov.au/public/sites/geojson"

FORECAST_TEMPLATE = "{forecast}: {locations}."
TOOT_TEMPLATE = "Pollution forecast for {area}:\n{forecasts}\n"
INTRO_TOOT_TEMPLATE = "Sydney beach pollution forecasts as of {when}.\n#sydney #pollution #ocean"
TIMEZONE = "Australia/Sydney"

areas = [
    {
        "name": "Eastern Suburbs",
        "file": "eastern_suburbs.geojson"
    },
    {
        "name": "Northern Beaches",
        "file": "northern_beaches.geojson"
    },
    {
        "name": "Botany",
        "file": "botany.geojson"
    },
    {
        "name": "The Shire",
        "file": "the_shire.geojson"
    },
    {
        "name": "Sydney Harbour",
        "file": "sydney_harbour.geojson"
    }
]

def build_area_data(area, beaches):
    with open(area["file"], 'r') as reader:
        file = reader.read()
        bounds = shapely.from_geojson(file)

        def reducer(carry, next):
            if (next["properties"]["pollutionForecast"] != "Forecast not available" and
                bounds.intersects(shapely.Point(next['geometry']["coordinates"]))):
                if next["properties"]["pollutionForecast"] not in carry:
                    carry[next["properties"]["pollutionForecast"]] = []
                carry[next["properties"]["pollutionForecast"]].append(next)
            return carry

        data = reduce(reducer, beaches["features"], {})
        return data

def build_toot(name, area_data):
    forecasts = []
    for forecast in area_data:
        locations = ", ".join([d["properties"]["siteName"] for d in area_data[forecast]])
        forecasts.append(FORECAST_TEMPLATE.format(forecast=forecast, locations=locations))
    forecasts = "\n".join(forecasts)
    toot = TOOT_TEMPLATE.format(area=area["name"], forecasts=forecasts)

    if len(toot) > max_len:
        toot = "{toot}…".format(toot=toot[0:max_len-1])
    return toot

def get_forecast_time(geojson):
    return datetime.fromisoformat(geojson["features"][0]["properties"]["pollutionForecastTimeStamp"])

def get_intro_toot(when):
    toot = INTRO_TOOT_TEMPLATE.format(when=when.astimezone(ZoneInfo(TIMEZONE)).strftime("%I:%M%p (%Z)"))
    return toot

def get_data():
    response = requests.get(URL)
    data = response.json()
    return data

def send_toot(toot, toot_id):
    # https://github.com/halcy/Mastodon.py
    # Create an instance of the Mastodon class
    mastodon = Mastodon(
        access_token=token,
        api_base_url=server
    )
    status = mastodon.status_post(toot, in_reply_to_id=toot_id)
    return status.id

if __name__ == "__main__":
    logger.info("Beginning run.")

    geojson = get_data()
    toot_id = None
    toots = []
    when = get_forecast_time(geojson)
    
    for area in areas:
        area_data = build_area_data(area, geojson)
        toot = build_toot(area, area_data)
        toots.append(toot)
    
    toot = get_intro_toot(when)
    logger.info(toot)
    toot_id = send_toot(toot, None)

    for toot in toots:
        send_toot(toot, toot_id)
        logger.info(toot)
