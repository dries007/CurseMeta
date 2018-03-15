from .taskhelpers import *
from ..models import HistoricRecord


@celery.task
@locked_task('periodic-keep_history')
def periodic_keep_history():
    # todo : implement
    logger.info('Gathering history...')

