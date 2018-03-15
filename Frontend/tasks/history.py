from .taskhelpers import *


@celery.task
@locked_task('periodic-keep_history')
def periodic_keep_history():
    logger.info('Gathering history...')
    pass
