from celery import Celery
from redis.exceptions import LockError

from CurseFeeds.BaseFeed import FeedException
from . import celery
from . import curse
from . import db
from . import redis_store
from .models import AddonModel
from .models import FileModel
from CurseFeeds import AddonsFeed, Timespan, GamesFeed


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(60*60, periodic_curse_login.s())

    sender.add_periodic_task(15*60, periodic_fill_missing_addons.s())

    sender.add_periodic_task(25*60, periodic_addon_feeds.s(Timespan.HOURLY.value))  # 25 mintes
    sender.add_periodic_task(11*60*60, periodic_addon_feeds.s(Timespan.DAILY.value))  # 11 hours
    sender.add_periodic_task(3*24*60*60, periodic_addon_feeds.s(Timespan.WEEKLY.value))  # 3 days
    sender.add_periodic_task(2*7*24*60*60, periodic_addon_feeds.s(Timespan.COMPLETE.value))  # 2 weeks (14 days)

    periodic_fill_missing_addons.apply_async(countdown=30)

    periodic_addon_feeds.apply_async([Timespan.COMPLETE.value], countdown=60)


@celery.task
def periodic_curse_login():
    return curse.login_client.checklogin()


@celery.task
def periodic_fill_missing_addons():
    # noinspection PyComparisonWithNone
    return sum(fill_missing_addon(x.id) for x in AddonModel.query.filter(AddonModel.name == None).all())


@celery.task
def periodic_addon_feed(timespan: str, gameid: int):
    lock = redis_store.lock('lock-periodic_addon_feed-{}-{}'.format(timespan, gameid), timeout=10*60)
    have_lock = False
    try:
        have_lock = lock.acquire(blocking=False)
        if have_lock:
            try:
                for addon in AddonsFeed(gameID=gameid, timespan=Timespan(timespan)).load_feed()['data']:
                    AddonModel.update(addon)
                    db.session.commit()
            except FeedException as e:
                print('Error checking feed', gameid, timespan, e)
            return True
        else:
            print('No lock, skipped', 'lock-periodic_addon_feed-{}-{}'.format(timespan, gameid))
            return False
    finally:
        if have_lock:
            try:
                lock.release()
            except LockError:
                pass


@celery.task
def periodic_addon_feeds(timespan: str):
    lock = redis_store.lock('lock-periodic_addon_feeds-{}'.format(timespan), timeout=10*60)
    have_lock = False
    try:
        have_lock = lock.acquire(blocking=False)
        if have_lock:
            for supported in filter(lambda x: x['SupportsAddons'], GamesFeed().load_feed()['data']):
                periodic_addon_feed.delay(timespan, supported['ID'])
            return True
        else:
            print('No lock, skipped ', 'lock-periodic_addon_feeds-{}'.format(timespan))
            return False
    finally:
        if have_lock:
            try:
                lock.release()
            except LockError:
                pass


@celery.task
def fill_missing_addon(addon_id: int):
    addon = AddonModel.query.get(addon_id)
    if addon is None or addon.name is None:
        curse.service.GetAddOn(addon_id)
        return True
    return False


@celery.task
def analyse_direct_result(name: str, inp: dict, outp: dict):
    # Deconstructs the return types of complex data returns into 'core' components for analysis
    if name == 'GetAddOn':
        AddonModel.update(outp)
    elif name == 'GetRepositoryMatchFromSlug':
        for f in outp['LatestFiles']:
            FileModel.update(outp['Id'], f)
    elif name == 'GetAddOnFile':
        FileModel.update(inp['addonID'], outp)
    elif name == 'v2GetAddOns':
        for f in outp:
            AddonModel.update(f)
    elif name == 'v2GetFingerprintMatches':
        for x in ('ExactMatches', 'PartialMatches'):
            o = outp[x]
            FileModel.update(o['Id'], o['File'])
            for f in o['LatestFiles']:
                FileModel.update(o['Id'], f)
    elif name == 'GetFuzzyMatches':
        for o in outp:
            FileModel.update(o['Id'], o['File'])
            for f in o['LatestFiles']:
                FileModel.update(o['Id'], f)
    elif name == 'GetAllFilesForAddOn':
        for o in outp:
            FileModel.update(inp['addOnID'], o)
    elif name == 'GetAddOnFiles':
        for o in outp:
            if o['Value']:
                FileModel.update(o['Key'], o['Value'])
    else:
        return False
    db.session.commit()
