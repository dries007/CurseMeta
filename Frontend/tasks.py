from celery import Celery

from . import curse
from . import celery


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(60*60, task_curse_login.s())


@celery.task
def task_curse_login():
    return curse.login_client.checklogin()
