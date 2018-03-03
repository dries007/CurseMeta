import logging
import mimetypes

from flask import Flask
from flask_script import Manager

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("MARKDOWN").setLevel(logging.INFO)

mimetypes.init()

app = Flask(__name__)
app.config.from_object('config')

manager = Manager(app)

from . import views

# fixme: It's impossible to catch HTTPException. Flask Bug #941 (https://github.com/pallets/flask/issues/941)
from werkzeug.exceptions import default_exceptions
for code, ex in default_exceptions.items():
    app.errorhandler(code)(views.any_error)

