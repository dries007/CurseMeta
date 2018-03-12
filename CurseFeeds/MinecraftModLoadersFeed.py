from .BaseFeed import BaseFeed


class MinecraftModLoadersFeed(BaseFeed):
    FEED_NAME = 'modloaders'
    FEED_FILENAME = FEED_NAME + '.json.bz2'
    COMPRESSED = True

    def __init__(self):
        super().__init__(432)
