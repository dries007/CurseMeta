from functools import wraps
from celery.utils.log import get_task_logger
from redis.exceptions import LockError

# noinspection PyUnresolvedReferences
from .. import celery
# noinspection PyUnresolvedReferences
from .. import db
from .. import redis_store


MAX_ADDONS_PER_REQUEST = 8000

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
