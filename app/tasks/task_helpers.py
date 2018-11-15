import requests

from CurseClient import MAX_ADDONS_PER_REQUEST

from celery.utils.log import get_task_logger

from .. import db
from ..models import AddonModel, AddonStatusEnum
from ..models import FileModel
from ..helpers import get_curse_api


logger = get_task_logger(__name__)


def request_all_files(id_: int):
    try:
        for x in get_curse_api('api/addon/%d/files' % id_).json():
            try:
                FileModel.update(id_, x)
            except:
                logger.exception('All files request inner error on {}'.format(x))
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            logger.info('404 on addon {}. Setting status to deleted to disable further polling.'.format(id_))
            try:
                x: AddonModel = AddonModel.query.get(id_)
                if x:
                    x.status = AddonStatusEnum.Deleted
                    db.session.commit()
            except:
                logger.exception('Error setting deleted on {}'.format(id_))
        else:
            logger.exception('Request HTTP error on {}'.format(id_))
    except:
        logger.exception('Request error on {}'.format(id_))


def request_addons_by_id(ids: [int]):
    # todo: also update the 'gameVersionLatestFiles' from this info
    total = len(ids)
    for i, id_ in enumerate(ids):
        if i % MAX_ADDONS_PER_REQUEST == 0:
            logger.info('Requesting addons... {} of {} ({:.2} %)'.format(i, total, 100 * i / total))
        try:
            x = get_curse_api('api/addon/%d' % id_).json()
            AddonModel.update(x)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.info('404 on addon {}. Setting status to deleted to disable further polling.'.format(id_))
                try:
                    x: AddonModel = AddonModel.query.get(id_)
                    if x:
                        x.status = AddonStatusEnum.Deleted
                        db.session.commit()
                except:
                    logger.exception('Error setting deleted on {}'.format(id_))
            else:
                logger.exception('Request HTTP error on {}'.format(id_))
        except:
            logger.exception('Request error on {}'.format(id_))


def request_addons(objects: [AddonModel]):
    # todo: also update the 'gameVersionLatestFiles' from this info
    total = len(objects)
    for i, obj in enumerate(objects):
        if i % MAX_ADDONS_PER_REQUEST == 0:
            logger.info('Requesting addons... {} of {} ({:.2} %)'.format(i, total, 100 * i / total))
        try:
            obj.update_direct(get_curse_api('api/addon/%d' % obj.addon_id).json())
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.info('404 on addon {}. Setting status to deleted to disable further polling.'.format(obj.addon_id))
                try:
                    obj.status = AddonStatusEnum.Deleted
                    db.session.commit()
                except:
                    logger.exception('Error setting deleted on {}'.format(obj.addon_id))
            else:
                logger.exception('Request HTTP error on {}'.format(obj.addon_id))
        except:
            logger.exception('Request error on {}'.format(obj.addon_id))
