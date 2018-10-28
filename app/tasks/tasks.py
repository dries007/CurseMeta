from CurseClient import MAX_ADDONS_PER_REQUEST

from celery.utils.log import get_task_logger

from .. import celery
from .. import db
from ..models import AddonModel
from ..models import FileModel
from ..helpers import get_curse_api
from ..helpers import post_curse_api


logger = get_task_logger(__name__)


@celery.task
def request_all_files(id_):
    logger.info('Requesting all files for id {}'.format(id_))
    try:
        for x in get_curse_api('api/addon/%d/files' % id_).json():
            FileModel.update(id_, x)
    except:
        logger.info('All files request error on {}'.format(id_))


@celery.task
def request_addons(ids):
    logger.info('Requesting addon {} ids'.format(len(ids)))
    for x in post_curse_api('api/addon', ids).json():
        o = AddonModel.update(x)
        # todo: also update the 'gameVersionLatestFiles' from this info
        ids.remove(o.addon_id)
    if ids:
        logger.info('Some ids are missing, deleting: {}'.format(ids))
        for id_ in ids:
            db.session.delete(AddonModel.query.get(id_))
        db.session.commit()


def request_addons_split(ids):
    for i in range(0, len(ids), MAX_ADDONS_PER_REQUEST):
        request_addons.delay(ids[i:i + MAX_ADDONS_PER_REQUEST])
