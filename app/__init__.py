import logging
import mimetypes
import datetime
import requests_cache

from celery import Celery
from flask import Flask
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_humanize import Humanize

import CurseClient

# Init code
logging.basicConfig(level=logging.WARN)

# Sanity please
mimetypes.init()

# Main Flask magic
app = Flask(__name__)
humanize = Humanize(app)
app.config.from_object('config')

if app.config.get('DEBUG', False):
    logging.basicConfig(logging=logging.DEBUG)

# Postgres DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Redis
# todo: make redis optional
redis_store = FlaskRedis(app)
redis_store.ping()  # Just to make sure the config is OK
# Monkey patch! To bypass use `with requests_cache.disabled():`
requests_cache.install_cache(backend='redis', expire_after=datetime.timedelta(hours=24), connection=redis_store)


# Curse Client
curse_login = CurseClient.LoginClient(app.config['CURSE_USER'], app.config['CURSE_PASS'], redis_store)


# Celery
celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

TaskBase = celery.Task


class ContextTask(TaskBase):
    abstract = True

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)


celery.Task = ContextTask


# Import all tasks (must be done for the periodic tasks to have effect)
from . import tasks

# Import all views
from . import models

# Import all views
from . import views
