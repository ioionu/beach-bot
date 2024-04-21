#!/usr/bin/env python
from mastodon import Mastodon
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import os
import json
from zoneinfo import ZoneInfo
from beachbot import BeachBot

logger = logging.getLogger("BeachBot")
logging.basicConfig(level=logging.INFO)

SERVER = os.environ.get("SERVER", "https://localhost")
TOKEN = os.environ.get("TOKEN", "insert coin")
TIMEZONE = os.environ.get("TIMEZONE", "Australia/Sydney")
RUNTIMES = os.environ.get("RUNTIMES", "23:18,23:21")
MAXLEN = os.environ.get("MAXLEN", 500)
URL = "https://api.beachwatch.nsw.gov.au/public/sites/geojson"
AREA_FILE = os.environ.get("AREA_FILE", "areas.json")

def runner():
    logger.info("Running scheduled beachbot")
    # https://github.com/halcy/Mastodon.py
    # Create an instance of the Mastodon class
    mastodon = Mastodon(
        access_token=TOKEN,
        api_base_url=SERVER
    )
    geojson = get_data(URL)
    areas = get_areas(AREA_FILE)
    beachbot = BeachBot(mastodon, areas, geojson, MAXLEN, TIMEZONE)
    beachbot.do_all_the_things()

def schedule(times: str, tz: str) -> None:
    sched = BlockingScheduler()
    tzinfo = ZoneInfo(tz)
    for time in times.split(","):
        time = time.split(":")
        logger.info("Scheduling for {hour}:{minute} ({tz})".format(hour=time[0], minute=time[1], tz=tz))
        sched.add_job(runner, 'cron', hour=time[0], minute=time[1], timezone=tzinfo)
    sched.start()

def get_data(url: str) -> list:
    response = requests.get(url)
    data = response.json()
    return data

def get_areas(file: str) -> list:
    with open(file, "r") as reader:
        return json.load(reader)

if __name__ == "__main__":
    logger.info("Beginning run.")
    schedule(RUNTIMES, TIMEZONE)
    logger.info("Be done.")
