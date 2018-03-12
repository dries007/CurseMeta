import enum

from .BaseFeed import BaseFeed


class Timespan(enum.Enum):
    COMPLETE = 'complete'
    HOURLY = 'hourly'
    DAILY = 'daily'
    WEEKLY = 'weekly'


class AddonsFeed(BaseFeed):
    FEED_NAME = 'addons'
    FEED_FILENAME = '%s.json.bz2'
    COMPRESSED = True

    def __init__(self, gameID: int, timespan: Timespan=Timespan.COMPLETE):
        super().__init__(gameID)
        self.timespan = timespan

    def get_feed_url(self) -> str:
        return super().get_feed_url() % self.timespan.value
