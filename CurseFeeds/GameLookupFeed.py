from .BaseFeed import BaseFeed


class GameLookupFeed(BaseFeed):
    FEED_NAME = 'gamelookups'
    FEED_FILENAME = FEED_NAME + '.json'
    COMPRESSED = False

    def __init__(self):
        super().__init__(None)
