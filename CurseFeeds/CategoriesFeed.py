from .BaseFeed import BaseFeed


class CategoriesFeed(BaseFeed):
    FEED_NAME = 'categories'
    FEED_FILENAME = FEED_NAME + '.json.bz2'
    COMPRESSED = True

    def __init__(self):
        super().__init__(None)
