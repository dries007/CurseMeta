from datetime import datetime
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

from functools import wraps
from celery.utils.log import get_task_logger
from redis.exceptions import LockError

from . import celery
from . import db
from . import curse_login
from . import redis_store


MAX_ADDONS_PER_REQUEST = 16000

logger = get_task_logger(__name__)


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


@celery.task
@locked_task('periodic-curse_login')
def periodic_curse_login():
    return curse_login.checklogin()
