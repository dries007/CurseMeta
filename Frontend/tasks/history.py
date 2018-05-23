import json
from datetime import datetime
from datetime import timedelta

from .taskhelpers import *
from ..models import AddonModel
from ..models import HistoricRecord


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
