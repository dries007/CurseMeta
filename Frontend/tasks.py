from datetime import datetime
from datetime import timedelta
from functools import wraps
from time import sleep

from celery import Celery
from celery.utils.log import get_task_logger
from redis import Redis
from redis.exceptions import LockError

from CurseFeeds import FeedException
from CurseFeeds import AddonsFeed
from CurseFeeds import Timespan
from CurseFeeds import GamesFeed

from . import app
from . import celery
from . import curse
from . import db
from . import redis_store
from .models import AddonModel
from .models import FileModel

redis_store: Redis = redis_store

logger = get_task_logger(__name__)

MAX_ADDONS_PER_REQUEST = 8000


def locked_task(name_: str or callable, timeout=10*60):
    def lock_task(fun):
        @wraps(fun)
        def outer(*args, **kwargs):
            if callable(name_):
                name = name_(*args, **kwargs)
            elif isinstance(name_, str):
                name = name_
            else:
                name = repr(name_)
            lock = redis_store.lock(name, timeout=timeout)
            have_lock = lock.acquire(blocking=False)
            if not have_lock:
                logger.info('Skipped locked task ' + name)
            else:
                try:
                    return fun(*args, **kwargs)
                finally:
                    if have_lock:
                        try:
                            lock.release()
                        except LockError as e:
                            logger.warn('LockError: {}'.format(e))
        return outer
    return lock_task


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(60*60, periodic_curse_login.s())

    sender.add_periodic_task(15*60, periodic_fill_missing_addons.s())

    if app.config['STAGING']:
        # How about we don't, there is no need for staging to be complete.
        # Manual runs are always possible via FlaskManager's shell
        return

    sender.add_periodic_task(25*60, periodic_addon_feeds.s(Timespan.HOURLY.value))  # 25 mintes
    sender.add_periodic_task(11*60*60, periodic_addon_feeds.s(Timespan.DAILY.value))  # 11 hours
    sender.add_periodic_task(3*24*60*60, periodic_addon_feeds.s(Timespan.WEEKLY.value))  # 3 days
    sender.add_periodic_task(2*7*24*60*60, periodic_addon_feeds.s(Timespan.COMPLETE.value))  # 2 weeks (14 days)

    sender.add_periodic_task(24*60*60, periodic_find_hidden_addons.s())  # daily

    sender.add_periodic_task(7*24*60*60, periodic_request_all_files.s())  # weekly

    periodic_fill_missing_addons.apply_async(countdown=30)

    # Mainly for staging, so we don't redo a full dl every time the env restart if it's been less than a day.
    # The hourly & daily's will get it.
    last = redis_store.get('periodic-addon_feeds-last-{}'.format(Timespan.COMPLETE.value))
    if last is None or datetime.now() - datetime.fromtimestamp(int(last)) > timedelta(days=1):
        periodic_addon_feeds.apply_async([Timespan.COMPLETE.value], countdown=60)

    last = redis_store.get('periodic-find_hidden_addons-last')
    if last is None or datetime.now() - datetime.fromtimestamp(int(last)) > timedelta(days=1):
        periodic_find_hidden_addons.apply_async(countdown=60*60)

    last = redis_store.get('periodic-request_all_files-last')
    if last is None or datetime.now() - datetime.fromtimestamp(int(last)) > timedelta(days=1):
        periodic_request_all_files.apply_async(countdown=4*60*60)


@celery.task
@locked_task('periodic-curse_login')
def periodic_curse_login():
    return curse.login_client.checklogin()


@celery.task
@locked_task('periodic-fill_missing_addons')
def periodic_fill_missing_addons():
    # noinspection PyComparisonWithNone
    missing_addon_ids = list(x[0] for x in db.session.query(AddonModel.addon_id).filter(AddonModel.name == None).all())
    if len(missing_addon_ids) == 0:
        return 0
    logger.info('Looking for {} addons with info missing'.format(len(missing_addon_ids)))
    found_count = 0
    for i in range(0, len(missing_addon_ids), MAX_ADDONS_PER_REQUEST):
        ids = missing_addon_ids[i:i + MAX_ADDONS_PER_REQUEST]
        logger.info('Batch {}, id {} to {}'.format(i, ids[0], ids[-1]))
        # noinspection PyBroadException
        try:
            addons = curse.service.v2GetAddOns(ids=ids)
            if addons is None:
                logger.info('No addons found in batch?')
                continue
            found_count += len(addons)
            logger.info('Found {} addons in batch'.format(len(addons)))
            db.session.commit()
        except Exception:
            logger.exception('Error in batch')
    logger.info('Filld {} missing addons'.format(found_count))
    return found_count


@celery.task
@locked_task('periodic-addon_feed-{}-lock-{}'.format, timeout=20*60)
def periodic_addon_feed(timespan: str, gameid: int):
    try:
        redis_store.set('periodic-addon_feed-{}-last-{}'.format(gameid, timespan), int(datetime.now().timestamp()))
        for addon in AddonsFeed(gameID=gameid, timespan=Timespan(timespan)).load_feed()['data']:
            AddonModel.update(addon)
            db.session.commit()
        return True
    except FeedException as e:
        print('Error checking feed', gameid, timespan, e)
    return False


@celery.task
@locked_task('periodic-addon_feeds-lock-{}'.format)
def periodic_addon_feeds(timespan: str):
    redis_store.set('periodic-addon_feeds-last-{}'.format(timespan), int(datetime.now().timestamp()))
    for supported in filter(lambda x: x['SupportsAddons'], GamesFeed().load_feed()['data']):
        periodic_addon_feed.delay(timespan, supported['ID'])
    return True


@celery.task
@locked_task('periodic-find_hidden_addons-lock', timeout=30*60)
def periodic_find_hidden_addons():
    redis_store.set('periodic-find_hidden_addons-last', int(datetime.now().timestamp()))
    start_id = redis_store.get('periodic-find_hidden_addons-start_id')
    start_id = int(start_id) if start_id is not None else 1
    from sqlalchemy import func
    end_id = db.session.query(func.max(AddonModel.addon_id)).scalar() + 1000
    logger.info('Finding hidden addons between id {} and {}'.format(start_id, end_id))
    known_ids = set(x[0] for x in db.session.query(AddonModel.addon_id).all())
    missing_ids = list(set(range(start_id, end_id)) - known_ids)
    if len(missing_ids) == 0:
        return 0
    logger.info('Looking for {} missing ids'.format(len(missing_ids)))
    sleep(10)
    last_found_id = start_id
    found_count = 0
    for i in range(0, len(missing_ids), MAX_ADDONS_PER_REQUEST):
        ids = missing_ids[i:i+MAX_ADDONS_PER_REQUEST]
        logger.info('Batch {}, id {} to {}'.format(i, ids[0], ids[-1]))
        # noinspection PyBroadException
        try:
            addons = curse.service.v2GetAddOns(ids=ids)
            if addons is None:
                logger.info('No ids found in batch.')
                continue
            found_count += len(addons)
            last_found_id = max(addons, key=lambda x: x['Id'])['Id']
            logger.info('Found {} addons in batch, last id {}'.format(len(addons), last_found_id))
            db.session.commit()
        except Exception:
            logger.exception('Error in batch')
    logger.info('Foud {} hidden addons, last id: {}'.format(found_count, last_found_id))
    redis_store.set('periodic-find_hidden_addons-start_id', last_found_id)
    return found_count


@celery.task
@locked_task('periodic-request_all_files-lock', timeout=2*60*60)
def periodic_request_all_files():
    redis_store.set('periodic-request_all_files-last', int(datetime.now().timestamp()))
    known_ids = list(x[0] for x in db.session.query(AddonModel.addon_id).all())
    for id_ in known_ids:
        # noinspection PyBroadException
        try:
            curse.service.GetAllFilesForAddOn(id_)
            db.session.commit()
        except Exception:
            logger.exception('Error in batch')


# @celery.task
# def fill_missing_addon(addon_id: int):
#     addon = AddonModel.query.get(addon_id)
#     if addon is None or addon.name is None:
#         curse.service.GetAddOn(addon_id)
#         return True
#     return False


@celery.task
def analyse_direct_result(name: str, inp: dict, outp: dict):
    # Deconstructs the return types of complex data returns into 'core' components for analysis
    # noinspection PyBroadException
    try:
        if name == 'GetAddOn':
            AddonModel.update(outp)
        elif name == 'GetRepositoryMatchFromSlug':
            if outp['LatestFiles'] is not None:
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
                if o['LatestFiles'] is not None:
                    for f in o['LatestFiles']:
                        FileModel.update(o['Id'], f)
        elif name == 'GetFuzzyMatches':
            for o in outp:
                FileModel.update(o['Id'], o['File'])
                if o['LatestFiles'] is not None:
                    for f in o['LatestFiles']:
                        FileModel.update(o['Id'], f)
        elif name == 'GetAllFilesForAddOn':
            for o in outp:
                FileModel.update(inp['addOnID'], o)
        elif name == 'GetAddOnFiles':
            for o in outp:
                if o['Value']:
                    for f in o['Value']:
                        FileModel.update(o['Key'], f)
        else:
            return False
        db.session.commit()
    except Exception:
        logger.exception('Error analyse_direct_result with {}: {} -> {}'.format(name, inp, outp))

