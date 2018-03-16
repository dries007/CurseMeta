from datetime import datetime
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

from .analysis import analyse_direct_result
from .feeds import periodic_addon_feed, periodic_addon_feeds, Timespan
from .find import periodic_fill_missing_addons, periodic_find_hidden_addons, periodic_request_all_files
from .find import manual_request_all_addons
from .history import periodic_keep_history
from .login import periodic_curse_login
from .. import celery
from .. import redis_store
from .. import app


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(60*60, periodic_curse_login.s())

    sender.add_periodic_task(15*60, periodic_fill_missing_addons.s())

    if app.config['STAGING']:
        # How about we don't, there is no need for staging to be complete.
        # Manual runs are always possible via FlaskManager's shell
        return

    sender.add_periodic_task(25*60, periodic_addon_feeds.s(Timespan.HOURLY.value))  # 25 minutes
    sender.add_periodic_task(11*60*60, periodic_addon_feeds.s(Timespan.DAILY.value))  # 11 hours
    sender.add_periodic_task(3*24*60*60, periodic_addon_feeds.s(Timespan.WEEKLY.value))  # 3 days
    sender.add_periodic_task(2*7*24*60*60, periodic_addon_feeds.s(Timespan.COMPLETE.value))  # 2 weeks (14 days)

    sender.add_periodic_task(24*60*60, periodic_find_hidden_addons.s())  # daily

    sender.add_periodic_task(7*24*60*60, periodic_request_all_files.s())  # weekly

    sender.add_periodic_task(crontab(minute='0', hour='*/4'), periodic_keep_history.s())  # every 4 hours at XX:00

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
