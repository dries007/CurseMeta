from datetime import datetime

from CurseFeeds import AddonsFeed
from CurseFeeds import FeedException
from CurseFeeds import GamesFeed
from CurseFeeds import Timespan
from .taskhelpers import *
from ..models import AddonModel


@celery.task
@locked_task('periodic-addon_feeds-lock-{}'.format)
def periodic_addon_feeds(timespan: str):
    redis_store.set('periodic-addon_feeds-last-{}'.format(timespan), int(datetime.now().timestamp()))
    for supported in filter(lambda x: x['SupportsAddons'], GamesFeed().load_feed()['data']):
        periodic_addon_feed.delay(timespan, supported['ID'])
    return True


@celery.task
@locked_task('periodic-addon_feed-{}-lock-{}'.format, timeout=20*60)
def periodic_addon_feed(timespan: str, gameid: int):
    try:
        redis_store.set('periodic-addon_feed-{}-last-{}'.format(gameid, timespan), int(datetime.now().timestamp()))

        feed = AddonsFeed(gameID=gameid, timespan=Timespan(timespan))
        last = redis_store.get('feed-timestamp-{}'.format(feed))
        latest = feed.get_latest_timestamp()
        if last is None or last < latest:
            for addon in feed.load_feed()['data']:
                AddonModel.update(addon)
                db.session.commit()
            redis_store.set('feed-timestamp-{}'.format(feed), latest)
            return True
        return False
    except FeedException as e:
        print('Error checking feed', gameid, timespan, e)
    return False
