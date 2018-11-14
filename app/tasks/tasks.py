import requests

from CurseClient import MAX_ADDONS_PER_REQUEST

from celery.utils.log import get_task_logger

from .. import celery
from .. import db
from ..models import AddonModel, AddonStatusEnum
from ..models import FileModel
from ..helpers import get_curse_api
from ..helpers import post_curse_api


logger = get_task_logger(__name__)


@celery.task
def request_all_files(id_):
    try:
        for x in get_curse_api('api/addon/%d/files' % id_).json():
            try:
                FileModel.update(id_, x)
            except:
                logger.exception('All files request inner error on {}'.format(x))
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            logger.info('404 on addon {}. Setting status to deleted to disable further polling.'.format(id_))
            x: AddonModel = AddonModel.query.get(id_)
            x.status = AddonStatusEnum.Deleted
            db.session.commit()
        else:
            logger.exception('All files request error on {}'.format(id_))
    except:
        logger.exception('All files request error on {}'.format(id_))


@celery.task
def request_addons(ids):
    try:
        for x in post_curse_api('api/addon', ids).json():
            try:
                AddonModel.update(x)
            except:
                logger.exception('Addons request inner error on {}'.format(x))

            #o = AddonModel.update(x)
            # todo: also update the 'gameVersionLatestFiles' from this info
            # ids.remove(o.addon_id)
        # if ids:
        #     logger.info('Some ids are missing, deleting {} ids'.format(len(ids)))
        #     for id_ in ids:
        #         AddonModel.query.filter_by(addon_id=id_).delete()
        #         db.session.commit()
    except:
        logger.exception('Addons request error on {}'.format(ids))


def request_addons_split(ids):
    for i in range(0, len(ids), MAX_ADDONS_PER_REQUEST):
        request_addons(ids[i:i + MAX_ADDONS_PER_REQUEST])
