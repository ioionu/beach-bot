#!/usr/bin/env python3
import os
import logging
from functools import reduce
import shapely
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.parser import parse
import random
import json

logger = logging.getLogger("BeachBot")
logging.basicConfig(level=logging.INFO)

server = os.environ.get("SERVER", "https://localhost")
token = os.environ.get("TOKEN", "insert coin")
MAXLEN = 500

URL = "https://api.beachwatch.nsw.gov.au/public/sites/geojson"

FORECAST_TEMPLATE = "{key} {forecast}: {locations}."
TOOT_TEMPLATE = "Pollution forecast for {area}:\n{forecasts}\n"
INTRO_TOOT_TEMPLATE = """Sydney beach pollution forecasts as of {when}.
Check https://www.beachwatch.nsw.gov.au for details.
#sydney #pollution #ocean
"""
TIMEZONE = "Australia/Sydney"

key = {
    "Likely": "❌",
    "Possible": "⚠️",
    "Unlikely": "✅"
}

class BeachBot:
    def __init__(self, mastadon, areas, geojson, maxlen, timezone):
        self.mastodon = mastadon
        self.areas = areas
        self.geojson = geojson
        self.maxlen = maxlen
        self.timezone = timezone

    def do_all_the_things(self):
        toot_id = None
        toots = []
        when = BeachBot.get_forecast_time(self.geojson)
        
        for area in self.areas:
            area_data = BeachBot.build_area_data(area, self.geojson)
            toot = self.build_toot(area, area_data)
            toots.append(toot)
        
        toot = BeachBot.get_intro_toot(when)
        logger.info(toot)
        toot_id = self.send_toot(toot, None)

        for toot in toots:
            self.send_toot(toot, toot_id)
            logger.info(toot)


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

    def build_toot(self, area, area_data):
        forecasts = []
        for forecast in area_data:
            locations = ", ".join([d["properties"]["siteName"] for d in area_data[forecast]])
            forecasts.append(FORECAST_TEMPLATE.format(forecast=forecast, locations=locations, key=key[forecast]))
        forecasts = "\n\n".join(forecasts)
        toot = TOOT_TEMPLATE.format(area=area["name"], forecasts=forecasts)

        if len(toot) > self.maxlen:
            toot = "{toot}…".format(toot=toot[0:self.maxlen-1])
        return toot

    def get_forecast_time(geojson):
        # nb py 3.9 fromisoformat does not parse ms in this date.
        return parse(geojson["features"][0]["properties"]["pollutionForecastTimeStamp"])

    def get_intro_toot(when):
        toot = INTRO_TOOT_TEMPLATE.format(when=when.astimezone(ZoneInfo(TIMEZONE)).strftime("%I:%M%p (%Z)"))
        return toot

    def send_toot(self, toot, toot_id):
        status = self.mastodon.status_post(toot, toot_id)
        return status.id