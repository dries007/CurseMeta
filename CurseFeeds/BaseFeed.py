import requests
import json


BASE_URL = 'https://clientupdate-v6.cursecdn.com'
VERSION = 10
MC_GAME_ID = 432


class FeedException(Exception):
    pass


class BaseFeed:
    FEED_NAME = None
    FEED_FILENAME = None
    COMPRESSED = True

    def __init__(self, gameID: int or None):
        self.gameID = gameID

    def get_feed_url(self) -> str:
        parts = (BASE_URL, 'feed', self.FEED_NAME, self.gameID, 'v%d' % VERSION, self.FEED_FILENAME)
        return '/'.join(map(str, filter(None, parts)))

    def load_feed(self) -> dict:
        url = self.get_feed_url()
        r = requests.get(url, timeout=60)
        if r.status_code // 100 != 2:
            raise FeedException('Code {} on {}'.format(r.status_code, url))
        data = r.content
        if self.COMPRESSED:
            import bz2
            data = bz2.decompress(data)
        return json.loads(data)

    def get_latest_timestamp(self) -> int:
        url = self.get_feed_url() + '.txt'
        return json.loads(requests.get(url, timeout=10).content)

    def __repr__(self) -> str:
        return '<{} gameID={}>'.format(self.FEED_NAME, self.gameID)
