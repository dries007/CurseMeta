import json
import flask
import requests
import werkzeug.datastructures
from functools import wraps

from app import curse_login


CURSE_HOST = 'https://addons-v2.forgesvc.net/'


def to_json_response(obj) -> flask.Response:
    return flask.Response(json.dumps(obj, separators=(',', ':')), mimetype="application/json")


def cache(time=4*60*60, browser_time=None):
    def decorator(f):
        @wraps(f)  # <- required to make __doc__ work, required for /docs
        def wrapper(*args, **kwargs):
            r = f(*args, **kwargs)
            if not isinstance(r, flask.Response):
                r = flask.Response(r)
            cc: werkzeug.datastructures.ResponseCacheControl = r.cache_control
            if time is None:
                cc.private = True
                cc.no_cache = True
            else:
                cc.public = True
                cc.max_age = time
                cc.s_maxage = time if browser_time is None else browser_time
            return r
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


def get_curse_api(url, params=None):
    """
    todo: better error handling(?)
    """
    r = requests.get(CURSE_HOST + url, params, timeout=60, headers=curse_login.get_headers())
    r.raise_for_status()
    return r


def post_curse_api(url, data):
    """
    todo: better error handling(?)
    """
    r = requests.post(CURSE_HOST + url, json=data, timeout=60, headers=curse_login.get_headers())
    r.raise_for_status()
    return r
