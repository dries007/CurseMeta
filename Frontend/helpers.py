import json

from . import app
from CurseClient.helpers import encode_json


def to_json_response(obj):
    return app.response_class(
        json.dumps(obj, default=encode_json),
        mimetype=app.config['JSONIFY_MIMETYPE']
    )
