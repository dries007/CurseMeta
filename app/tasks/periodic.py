import requests_cache

from sqlalchemy import func
from celery.utils.log import get_task_logger
from datetime import datetime
from datetime import timedelta
from influxdb import InfluxDBClient

from .. import curse_login
from .. import celery
from .. import db
from .. import app
from .. import redis_store
from ..models import AddonModel, AddonStatusEnum

from .task_helpers import request_addons
from .task_helpers import request_addons_by_id
from .task_helpers import request_all_files


logger = get_task_logger(__name__)


@celery.task
def p_curse_checklogin():
    return curse_login.renew_session()


@celery.task
def p_remove_expired_caches():
    return requests_cache.core.remove_expired_responses()


@celery.task
def p_fill_incomplete_addons():
    request_addons(AddonModel.query.filter(AddonModel.name == None).all())


@celery.task
def p_find_hidden_addons():
    end_id: int = db.session.query(func.max(AddonModel.addon_id)).scalar() + 1000
    known_ids: {int} = {x for x, in db.session.query(AddonModel.addon_id).all()}
    # tried = redis_store.get('cursemeta-periodic-failedById') or set()
    # ids = list(set(range(end_id)) - known_ids - tried)
    # logger.info('Looking for hidden addons until id {}, missing {} ids. Skipping {} redis keys.'.format(end_id, len(ids), len(tried)))
    ids = list(set(range(end_id)) - known_ids)
    logger.info('Looking for hidden addons until id {}, missing {} ids.'.format(end_id, len(ids)))
    request_addons_by_id(ids)


@celery.task
def p_update_all_files():
    ids: [(int, )] = db.session.query(AddonModel.addon_id).filter(AddonModel.game_id != None, AddonModel.status != AddonStatusEnum.Deleted).all()
    for i, (addon_id, ) in enumerate(ids):
        if i % 1000 == 0:
            logger.info('p_update_all_files {} of {} ({} %) '.format(i, len(ids), 100*i/len(ids)))
        request_all_files(addon_id)


@celery.task
def p_update_all_addons():
    threshold = datetime.now() - timedelta(hours=2)
    request_addons(AddonModel.query.filter(AddonModel.last_update < threshold, AddonModel.game_id != None, AddonModel.status != AddonStatusEnum.Deleted).all())


@celery.task
def p_keep_history():
    # now = datetime.now().date()
    addons: [AddonModel] = AddonModel.query.filter(AddonModel.game_id != None, AddonModel.downloads >= 1000, AddonModel.status != AddonStatusEnum.Deleted).all()
    # db.session.add_all([HistoricDayRecord(now, addon) for addon in addons])
    # db.session.commit()
    client = InfluxDBClient(database=app.config['INFLUX_DB'])
    client.write_points([
        {
            "measurement": "cursemeta",
            "tags": {
                'id': addon.addon_id,
                'slug': addon.slug,
                'author': addon.primary_author_name,
                'game': addon.game_id,
            },
            "time": addon.last_update.isoformat(),
            "fields": {
                "downloads": addon.downloads,
                "score": addon.score,
            }
        } for addon in addons])
