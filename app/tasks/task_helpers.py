import requests

from CurseClient import MAX_ADDONS_PER_REQUEST

from celery.utils.log import get_task_logger

from .. import db
from .. import redis_store
from ..models import AddonModel, AddonStatusEnum
from ..models import FileModel
from ..helpers import get_curse_api
from ..helpers import post_curse_api


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
        if i % 1000 == 0:
            logger.info('Requesting addons... {} of {} ({:.2} %)'.format(i, total, 100 * i / total))
        try:
            x = get_curse_api('api/addon/%d' % id_).json()
            AddonModel.update(x)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                try:
                    x: AddonModel = AddonModel.query.get(id_)
                    if x:
                        x.status = AddonStatusEnum.Deleted
                        db.session.commit()
                    # else:
                        # redis_store.sadd('cursemeta-periodic-failedById', id_)
                except:
                    logger.exception('Error setting deleted on {}'.format(id_))
            else:
                logger.exception('Request HTTP error on {}'.format(id_))
        except:
            logger.exception('Request error on {}'.format(id_))


def request_addons(objects: [AddonModel]):
    # todo: also update the 'gameVersionLatestFiles' from this info
    total = len(objects)
    for i in range(0, total, 5000):
        logger.info('Requesting addons... {} of {} ({:.2} %)'.format(i, total, 100 * i / total))
        try:
            subsection = {x.addon_id: x for x in objects[i:i + 5000]}
            raw_data = post_curse_api('api/addon', list(subsection.keys())).json()
            # logger.info('Posted, got back {} items'.format(len(raw_data)))
            for x in raw_data:
                try:
                    subsection[x['id']].update_direct(x, commit=False, skip_some=True)
                    del subsection[x['id']]
                except:
                    logger.exception('Error updating data after request on {}'.format(x))
            # logger.info('Marking {} addons as deleted'.format(len(subsection)))
            for x in subsection.values():
                x.status = AddonStatusEnum.Deleted
            db.session.commit()
        except:
            logger.exception('Request error on range {}'.format(i))

