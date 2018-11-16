from celery import Celery
from celery.schedules import crontab

from functools import wraps
from celery.utils.log import get_task_logger
from redis.exceptions import LockError

from CurseClient import MAX_ADDONS_PER_REQUEST
from .. import celery
from .. import redis_store
from ..models import *


from .periodic import p_curse_checklogin
from .periodic import p_remove_expired_caches
from .periodic import p_fill_incomplete_addons
from .periodic import p_find_hidden_addons
from .periodic import p_update_all_files
from .periodic import p_update_all_addons
from .periodic import p_keep_history


logger = get_task_logger(__name__)


def locked_task(name_: str or callable, timeout=10*60):
    """
    todo: Re-evaluate usefulness.
    todo: Autodetect name based on underlying function name.
    :param name_:
    :param timeout:
    :return:
    """
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

# def _delta_dl(records: {int: HistoricRecord}, x: AddonModel):
#     cur = x.downloads
#     if cur is None:
#         return 0
#     old = records[x.addon_id].downloads if x.addon_id in records else None
#     return cur if old is None else cur - old
#
#
# def _download_feed(records: {int: HistoricRecord}, addons: [AddonModel], game_id: int):
#     return {x.addon_id: _delta_dl(records, x) for x in addons if x.game_id == game_id}


FEEDS_INTERVALS = {'daily': 1, 'weekly': 7, 'monthly': 30}


@celery.task
def manual_addons():
    from .task_helpers import request_addons
    request_addons(AddonModel.query.all())


@celery.task
def manual_files():
    from .task_helpers import request_all_files
    ids: [(int,)] = db.session.query(AddonModel.addon_id).all()
    for i, (addon_id,) in enumerate(ids):
        if i % 1000 == 0:
            logger.info('p_update_all_files {} of {} ({} %) '.format(i, len(ids), 100 * i / len(ids)))
        request_all_files(addon_id)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(15 * 60, p_remove_expired_caches.s())
    sender.add_periodic_task(15 * 60, p_curse_checklogin.s())

    sender.add_periodic_task(15 * 60, p_update_all_addons.s())

    sender.add_periodic_task(45 * 60, p_fill_incomplete_addons.s())

    sender.add_periodic_task(6 * 60 * 60, p_update_all_files.s())
    sender.add_periodic_task(24 * 60 * 60, p_find_hidden_addons.s())

    sender.add_periodic_task(crontab(minute='0'), p_keep_history.s())

