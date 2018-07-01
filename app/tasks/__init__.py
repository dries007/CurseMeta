import json
from datetime import datetime
from datetime import timedelta

import requests
import requests_cache
from celery import Celery
from celery.schedules import crontab

from functools import wraps
from celery.utils.log import get_task_logger
from redis.exceptions import LockError

from .. import celery
from .. import db
from .. import curse_login
from .. import redis_store
from ..models import *
from ..helpers import get_curse_api
from ..helpers import post_curse_api


logger = get_task_logger(__name__)
MAX_ADDONS_PER_REQUEST = 16000


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


def get_dlfeed_key(game_id, interval):
    return 'history-feed-{}-{}'.format(game_id, interval)


def _delta_dl(records: {int: HistoricRecord}, x: AddonModel):
    cur = x.downloads
    if cur is None:
        return 0
    old = records[x.addon_id].downloads if x.addon_id in records else None
    return cur if old is None else cur - old


def _download_feed(records: {int: HistoricRecord}, addons: [AddonModel], game_id: int):
    return {x.addon_id: _delta_dl(records, x) for x in addons if x.game_id == game_id}


FEEDS_INTERVALS = {'daily': 1, 'weekly': 7, 'monthly': 30}


@celery.task
@locked_task('periodic-curse_login')
def periodic_curse_login():
    return curse_login.checklogin()


@celery.task
def periodic_remove_expired_caches():
    return requests_cache.remove_expired_responses()


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
    missing_ids = sorted(list(set(range(start_id, end_id)) - known_ids))
    if len(missing_ids) == 0:
        return 0
    logger.info('Looking for {} missing ids'.format(len(missing_ids)))
    last_found_id = start_id
    found_count = 0
    for i in range(0, len(missing_ids), MAX_ADDONS_PER_REQUEST):
        ids = missing_ids[i:i + MAX_ADDONS_PER_REQUEST]
        logger.info('Batch {}, id {} to {}'.format(i / MAX_ADDONS_PER_REQUEST, ids[0], ids[-1]))
        # noinspection PyBroadException
        try:
            data = post_curse_api('api/addon', ids).json()
            if data is None or len(data) == 0:
                logger.info('No addons found in batch?')
                continue
            for x in data:
                AddonModel.update(x)
            found_count += len(data)
            last_found_id = max(data, key=lambda x: x['id'])['id']
            logger.info('Found {} addons in batch, last id {}'.format(len(data), last_found_id))
        except Exception:
            logger.exception('Error in batch')
    logger.info('Found {} hidden addons, last id: {}'.format(found_count, last_found_id))
    redis_store.set('periodic-find_hidden_addons-start_id', last_found_id)
    return found_count


@celery.task
@locked_task('periodic-fill_missing_addons')
def periodic_fill_missing_addons():
    # noinspection PyComparisonWithNone
    missing_addon_ids = sorted(x[0] for x in db.session.query(AddonModel.addon_id).filter(AddonModel.name == None).all())
    if len(missing_addon_ids) == 0:
        return 0
    logger.info('Looking for {} addons with info missing'.format(len(missing_addon_ids)))
    found_count = 0
    for i in range(0, len(missing_addon_ids), MAX_ADDONS_PER_REQUEST):
        ids = missing_addon_ids[i:i + MAX_ADDONS_PER_REQUEST]
        logger.info('Batch {}, id {} to {}'.format(i / MAX_ADDONS_PER_REQUEST, ids[0], ids[-1]))
        # noinspection PyBroadException
        try:
            data = post_curse_api('api/addon', ids).json()
            if data is None or len(data) == 0:
                logger.info('No addons found in batch?')
                continue
            for x in data:
                AddonModel.update(x)
            found_count += len(data)
            logger.info('Found {} addons in batch'.format(len(data)))
        except Exception:
            logger.exception('Error in batch')
    logger.info('Filled {} missing addons'.format(found_count))
    return found_count


@celery.task
@locked_task('periodic-request_all_files-lock', timeout=2*60*60)
def periodic_request_all_files():
    redis_store.set('periodic-request_all_files-last', int(datetime.now().timestamp()))
    known_ids = sorted(x[0] for x in db.session.query(AddonModel.addon_id).all())
    for id in known_ids:
        logger.info('Getting all files for {}'.format(id))
        # noinspection PyBroadException
        try:
            data = get_curse_api('api/addon/%d/files' % id).json()
            for x in data:
                FileModel.update(id, x)
        except requests.RequestException:
            logger.exception('Error in batch')


@celery.task
def manual_request_all_addons():
    known_ids = sorted(x[0] for x in db.session.query(AddonModel.addon_id).all())
    logger.info('Requesting info on all {} addons'.format(len(known_ids)))
    for id in known_ids:
        # noinspection PyBroadException
        try:
            data = get_curse_api('api/addon/%d/files' % id).json()
            for x in data:
                FileModel.update(id, x)
        except requests.RequestException:
            logger.exception('Error in batch')


@celery.task
@locked_task('periodic-keep_history')
def periodic_keep_history():
    now = datetime.now()
    logger.info('Starting keeping history for timestamp {}'.format(now))

    records = {x.addon_id: x for x in HistoricRecord.get_all_last_before(timestamp=now)}
    addons: [AddonModel] = AddonModel.query.filter(AddonModel.game_id != None).all()
    n = len(addons)
    logger.info('Currently have history for {} out of {} addons'.format(len(records), n))

    new_count = 0
    update_count = 0
    records = []
    for i, addon in enumerate(addons):
        if i % 5000 == 0:
            logger.info('Working on addon {} / {} ({:.2f}%) got {} new {} updated so far.'.format(i, n, i/n*100, new_count, update_count))
        # addon: AddonModel
        if addon.addon_id not in records:
            records.append(HistoricRecord(now, addon.addon_id, addon.downloads, addon.score))
            new_count += 1
        else:
            current: HistoricRecord = records[addon.addon_id]
            if current.downloads != addon.downloads or current.score != addon.score:
                records.append(HistoricRecord(now, addon.addon_id, addon.downloads, addon.score))
                update_count += 1
    db.session.add_all(records)
    db.session.commit()

    logger.info('{} new, {} updated, timestamp {}'.format(new_count, update_count, now))

    periodic_generate_history_feed.delay()

    return new_count, update_count


@celery.task
@locked_task('periodic-generate_history_feed')
def periodic_generate_history_feed():
    now = datetime.now()
    addons: [AddonModel] = AddonModel.query.filter(AddonModel.game_id != None).all()
    game_ids = set(x.game_id for x in addons)
    for name, days in FEEDS_INTERVALS.items():
        records = {x.addon_id: x for x in HistoricRecord.get_all_last_before(timestamp=now - timedelta(days=days))}
        for game_id in game_ids:
            redis_store.set(get_dlfeed_key(game_id, name), json.dumps(_download_feed(records, addons, game_id)))
    redis_store.sadd('history-game_ids', *game_ids)
    redis_store.set('history-timestamp', int(now.timestamp()))


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(60 * 60, periodic_curse_login.s())
    sender.add_periodic_task(60 * 60, periodic_remove_expired_caches.s())

    sender.add_periodic_task(15 * 60, periodic_fill_missing_addons.s())

    # todo: replacement for periodic feeds

    sender.add_periodic_task(24 * 60 * 60, periodic_find_hidden_addons.s())  # daily

    sender.add_periodic_task(7 * 24 * 60 * 60, periodic_request_all_files.s())  # weekly

    sender.add_periodic_task(crontab(minute='0', hour='*'), periodic_keep_history.s())  # every hour at XX:00

    periodic_fill_missing_addons.apply_async(countdown=30)

    # Mainly for staging, so we don't redo a full dl every time the env restart if it's been less than a day.
    # The hourly & daily's will get it.
    last = redis_store.get('periodic-find_hidden_addons-last')
    if last is None or datetime.now() - datetime.fromtimestamp(int(last)) > timedelta(days=1):
        periodic_find_hidden_addons.apply_async(countdown=60 * 60)

    last = redis_store.get('periodic-request_all_files-last')
    if last is None or datetime.now() - datetime.fromtimestamp(int(last)) > timedelta(days=1):
        periodic_request_all_files.apply_async(countdown=4 * 60 * 60)
