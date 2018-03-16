from datetime import datetime

from .taskhelpers import *
from ..models import AddonModel
from ..models import HistoricRecord


@celery.task
@locked_task('periodic-keep_history')
def periodic_keep_history():
    now = datetime.now()
    logger.info('Starting keeping history for timestamp {}'.format(now))
    s = sum(HistoricRecord.add_from_model(now, addon) for addon in AddonModel.query.all())
    logger.info('Added {} new history records, with timestamp {}'.format(s, now))
    return s
