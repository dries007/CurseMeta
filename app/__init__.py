import logging
import mimetypes

import flask

from celery import Celery
from flask import Flask
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import CurseClient

# Init code
logging.basicConfig(level=logging.WARN)

# Sanity please
mimetypes.init()

# Main Flask magic
app = flask.Flask(__name__)
app.config.from_object('config')

if app.config.get('DEBUG', False):
    logging.basicConfig(logging=logging.DEBUG)

# Postgres DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Redis
redis_store = FlaskRedis(app)
redis_store.ping()  # Just to make sure the config is OK

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

from .tasks import *
from .routes import *
from .models import *

