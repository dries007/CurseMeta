import collections
import json
import flask
import werkzeug.datastructures

from CurseClient.helpers import encode_json


Documentation = collections.namedtuple('Documentation', ['rules', 'inp', 'outp'])


def to_json_response(obj) -> flask.Response:
    return flask.Response(json.dumps(obj, default=encode_json, separators=(',', ':')), mimetype="application/json")


def cache(time=4*60*60):
    def decorator(f):
        def wrapper(*args, **kwargs):
            r: flask.Response = f(*args, **kwargs)
            cc: werkzeug.datastructures.ResponseCacheControl = r.cache_control
            if time is None:
                cc.private = True
                cc.no_cache = True
            else:
                cc.public = True
                cc.max_age = time
            return r
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
