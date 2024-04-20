import logging
import random

logger = logging.getLogger("BeachBot")
logging.basicConfig(level=logging.INFO)

class FakeMastodon:

    class Status:
        def __init__(self):
            self.id = random.randrange(0, 100, 1)

    def __init__(self, access_token, api_base_url):
        pass

    def status_post(self, text, in_reply_to_id=None):
        logger.info(text)
        return FakeMastodon.Status()
