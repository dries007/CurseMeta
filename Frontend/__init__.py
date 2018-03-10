import logging
import mimetypes

import CurseClient

from celery import Celery
from flask import Flask
from flask_script import Manager
from flask_redis import FlaskRedis

# Init code
logging.basicConfig(level=logging.WARN)
mimetypes.init()

# Flask app init & config
app = Flask(__name__)
app.config.from_object('config')

if app.config.get('STAGING', False):
    logging.basicConfig(logging=logging.DEBUG)

# Manager (for CLI)
manager = Manager(app)

# Redis
redis_store = FlaskRedis(app)
redis_store.ping()  # Just to make sure the config is OK

# Curse Client
curse = CurseClient.CurseClient(app.config['CURSE_USER'], app.config['CURSE_PASS'], redis_store)

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
from . import views

# Catch-all error handler
# fixme: It's impossible to catch HTTPException. Flask Bug #941 (https://github.com/pallets/flask/issues/941)
from werkzeug.exceptions import default_exceptions
for code, ex in default_exceptions.items():
    app.errorhandler(code)(views.any_error)

