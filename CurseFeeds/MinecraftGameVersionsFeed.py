from .BaseFeed import BaseFeed


class MinecraftGameVersionsFeed(BaseFeed):
    FEED_NAME = 'gameversions'
    FEED_FILENAME = FEED_NAME + '.json.bz2'
    COMPRESSED = True

    def __init__(self):
        super().__init__(432)
