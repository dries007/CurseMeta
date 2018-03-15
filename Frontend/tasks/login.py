from .taskhelpers import *

from .. import curse


@celery.task
@locked_task('periodic-curse_login')
def periodic_curse_login():
    return curse.login_client.checklogin()
