from .BaseFeed import BaseFeed


class GamesFeed(BaseFeed):
    FEED_NAME = 'games'
    FEED_FILENAME = FEED_NAME + '.json.bz2'
    COMPRESSED = True

    def __init__(self):
        super().__init__(None)
