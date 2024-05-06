#!/usr/bin/env python
from unittest.mock import MagicMock
from unittest import TestCase
import unittest

from shapely.measurement import area
from BeachMap import BeachMap
from BeachBot import BeachBot
from mastodon import Mastodon
import json

def load_date() -> list:
    with open("areas.json", "r") as reader:
        geojson = json.load(reader)
        return geojson

class TestBeachBot(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mastodon = Mastodon(
            access_token="token",
            api_base_url="server"
        )
        # cls.mastodon.status_post = MagicMock(return_value={'id': 12345})
        # cls.mastodon.media_post = MagicMock(return_value={'id': 54321})
        cls.mastodon.status_post = MagicMock()
        cls.mastodon.media_post = MagicMock()

        with open("areas.json", "r") as reader:
            cls.areas = json.load(reader)
        
        with open("tests/geojson-fixture-tidy.json", "r") as reader:
            cls.geojson = json.load(reader)

    def testToot(self):
        bb = BeachBot(self.mastodon, self.areas, self.geojson, 500, "Australia/Sydney")
        bb.do_all_the_things()
        # TODO: Confirm called with:
        # 'Sydney beach pollution forecasts as of 01:30PM (AEST).\nCheck https://www.beachwatch.nsw.gov.au for details.\n#sydney #pollution #ocean\n'
        # 'Pollution forecast for Eastern Suburbs:\n✅ Unlikely: Bondi Beach.\n'
        self.mastodon.status_post.assert_called()

    @classmethod
    def tearDownClass(cls):
        pass

class TestBeachMap(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mastodon = Mastodon(
            access_token="token",
            api_base_url="server"
        )
        cls.mastodon.status_post = MagicMock({'id': 12345})
        cls.mastodon.media_post = MagicMock({'id': 54321})

        with open("areas.json", "r") as reader:
            cls.areas = json.load(reader)
        
        with open("tests/geojson-fixture.json", "r") as reader:
            cls.geojson = json.load(reader)

    def testMap(self):
        bb = BeachBot(self.mastodon, self.areas, self.geojson, 500, "Australia/Sydney")

        areas_data = [
            {
                "name": area["name"],
                "data": bb.build_area_data(area, bb.geojson)
            }
            for area in bb.areas
        ]

        for area_data in areas_data:
            # Create BeachMap instance using area_data
            # if area_data["name"] != "Sydney Harbour":
            #     continue
            bm = BeachMap(area_data['name'], area_data['data'])
            bm.draw_map()


        print(areas_data)

if __name__ == "__main__":
    unittest.main()