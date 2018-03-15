from datetime import datetime

from .taskhelpers import *
from .. import curse
from .. import db
from ..models import AddonModel


@celery.task
@locked_task('periodic-find_hidden_addons-lock', timeout=30*60)
def periodic_find_hidden_addons():
    redis_store.set('periodic-find_hidden_addons-last', int(datetime.now().timestamp()))
    start_id = redis_store.get('periodic-find_hidden_addons-start_id')
    start_id = int(start_id) if start_id is not None else 1
    from sqlalchemy import func
    end_id = db.session.query(func.max(AddonModel.addon_id)).scalar() + 1000
    logger.info('Finding hidden addons between id {} and {}'.format(start_id, end_id))
    known_ids = set(x[0] for x in db.session.query(AddonModel.addon_id).all())
    missing_ids = sorted(list(set(range(start_id, end_id)) - known_ids))
    if len(missing_ids) == 0:
        return 0
    logger.info('Looking for {} missing ids'.format(len(missing_ids)))
    last_found_id = start_id
    found_count = 0
    for i in range(0, len(missing_ids), MAX_ADDONS_PER_REQUEST):
        ids = missing_ids[i:i+MAX_ADDONS_PER_REQUEST]
        logger.info('Batch {}, id {} to {}'.format(i/MAX_ADDONS_PER_REQUEST, ids[0], ids[-1]))
        # noinspection PyBroadException
        try:
            addons = curse.service.v2GetAddOns(ids=ids)
            if addons is None:
                logger.info('No ids found in batch.')
                continue
            found_count += len(addons)
            last_found_id = max(addons, key=lambda x: x['Id'])['Id']
            logger.info('Found {} addons in batch, last id {}'.format(len(addons), last_found_id))
            db.session.commit()
        except Exception:
            logger.exception('Error in batch')
    logger.info('Foud {} hidden addons, last id: {}'.format(found_count, last_found_id))
    redis_store.set('periodic-find_hidden_addons-start_id', last_found_id)
    return found_count


@celery.task
@locked_task('periodic-fill_missing_addons')
def periodic_fill_missing_addons():
    # noinspection PyComparisonWithNone
    missing_addon_ids = sorted(x[0] for x in db.session.query(AddonModel.addon_id).filter(AddonModel.name == None).all())
    if len(missing_addon_ids) == 0:
        return 0
    logger.info('Looking for {} addons with info missing'.format(len(missing_addon_ids)))
    found_count = 0
    for i in range(0, len(missing_addon_ids), MAX_ADDONS_PER_REQUEST):
        ids = missing_addon_ids[i:i + MAX_ADDONS_PER_REQUEST]
        logger.info('Batch {}, id {} to {}'.format(i/MAX_ADDONS_PER_REQUEST, ids[0], ids[-1]))
        # noinspection PyBroadException
        try:
            addons = curse.service.v2GetAddOns(ids=ids)
            if addons is None:
                logger.info('No addons found in batch?')
                continue
            found_count += len(addons)
            logger.info('Found {} addons in batch'.format(len(addons)))
            db.session.commit()
        except Exception:
            logger.exception('Error in batch')
    logger.info('Filld {} missing addons'.format(found_count))
    return found_count


@celery.task
@locked_task('periodic-request_all_files-lock', timeout=2*60*60)
def periodic_request_all_files():
    redis_store.set('periodic-request_all_files-last', int(datetime.now().timestamp()))
    known_ids = sorted(x[0] for x in db.session.query(AddonModel.addon_id).all())
    for id_ in known_ids:
        # noinspection PyBroadException
        try:
            curse.service.GetAllFilesForAddOn(id_)
            db.session.commit()
        except Exception:
            logger.exception('Error in batch')


@celery.task
def manual_request_all_addons():
    known_ids = sorted(x[0] for x in db.session.query(AddonModel.addon_id).all())
    logger.info('Requesting info on all {} addons'.format(len(known_ids)))
    for i in range(0, len(known_ids), MAX_ADDONS_PER_REQUEST):
        ids = known_ids[i:i + MAX_ADDONS_PER_REQUEST]
        logger.info('Batch {}, id {} to {}'.format(i/MAX_ADDONS_PER_REQUEST, ids[0], ids[-1]))
        # noinspection PyBroadException
        try:
            addons = curse.service.v2GetAddOns(ids=ids)
            if addons is None:
                logger.info('No addons found in batch?')
                continue
            logger.info('Found {} addons in batch'.format(len(addons)))
            db.session.commit()
        except Exception:
            logger.exception('Error in batch')

