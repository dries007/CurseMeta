import requests_cache

from sqlalchemy import func
from celery.utils.log import get_task_logger
from datetime import datetime
from datetime import timedelta

from CurseClient import MAX_ADDONS_PER_REQUEST

from .. import curse_login
from .. import celery
from .. import db
from ..models import AddonModel

from .tasks import request_addons_split
from .tasks import request_all_files


logger = get_task_logger(__name__)


@celery.task
def p_curse_checklogin():
    return curse_login.renew_session()


@celery.task
def p_remove_expired_caches():
    return requests_cache.core.remove_expired_responses()


@celery.task
def p_fill_incomplete_addons():
    # `AddonModel.name == None` is required.
    ids: [int] = [x.addon_id for x in AddonModel.query.filter(AddonModel.name == None).all()]
    request_addons_split(ids)


@celery.task
def p_find_hidden_addons():
    end_id: int = db.session.query(func.max(AddonModel.addon_id)).scalar() + MAX_ADDONS_PER_REQUEST // 4
    known_ids: {int} = {x.addon_id for x in AddonModel.query.all()}
    ids = list(set(range(end_id)) - known_ids)
    logger.info('Looking for hidden addons until id {}, missing {} ids.'.format(end_id, len(ids)))
    request_addons_split(ids)


@celery.task
def p_update_all_files():
    ids: [int] = [x.addon_id for x in AddonModel.query.all()]
    for addon_id in ids:
        request_all_files(addon_id)


@celery.task
def p_update_all_addons():
    threshold = datetime.now() - timedelta(hours=1)
    ids: [int] = [x.addon_id for x in AddonModel.query.filter(AddonModel.last_update < threshold).all()]
    request_addons_split(ids)
