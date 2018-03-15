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
    # todo: store latest timestamp from the feed in redis and use that to check if we should even download the feed.
    # todo: if error, just skip
    try:
        redis_store.set('periodic-addon_feed-{}-last-{}'.format(gameid, timespan), int(datetime.now().timestamp()))
        for addon in AddonsFeed(gameID=gameid, timespan=Timespan(timespan)).load_feed()['data']:
            AddonModel.update(addon)
            db.session.commit()
        return True
    except FeedException as e:
        print('Error checking feed', gameid, timespan, e)
    return False
