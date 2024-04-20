#!/usr/bin/env python
from unittest.mock import Mock
from unittest import TestCase
import unittest
from mastodon import Mastodon
from beachbot import BeachBot
import json


class TestBeach(TestCase):

    @classmethod
    def setUpClass(cls):
        Mastodon = Mock()

        cls.mastodon = Mastodon(
            access_token="token",
            api_base_url="server"
        )

        with open("areas.json", "r") as reader:
            cls.areas = json.load(reader)

        with open("tests/geojson-fixture.json", "r") as reader:
            cls.geojson = json.load(reader)


    def testToot(self):
        bb = BeachBot(self.mastodon, self.areas, self.geojson, 500, "Australia/Sydney")
        bb.do_all_the_things()
    
    @classmethod
    def tearDownClass(cls):
        pass

if __name__ == "__main__":
    unittest.main()