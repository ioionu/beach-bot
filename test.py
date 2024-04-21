#!/usr/bin/env python
from unittest.mock import MagicMock
from unittest import TestCase
import unittest
from beachbot import BeachBot
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
        cls.mastodon.status_post = MagicMock({'id': 12345})

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

if __name__ == "__main__":
    unittest.main()