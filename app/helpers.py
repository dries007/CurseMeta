import json
import flask
import requests
import werkzeug.datastructures
import werkzeug.routing
from functools import wraps

from . import app
from . import curse_login


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
    try:
        r = requests.get(CURSE_HOST + url, params, timeout=60, headers=curse_login.get_headers())
        r.raise_for_status()
    except ConnectionError or requests.RequestException:
        r = requests.get(CURSE_HOST + url, params, timeout=60, headers=curse_login.get_headers())
        r.raise_for_status()
    return r


def post_curse_api(url, data):
    """
    todo: better error handling(?)
    """
    try:
        r = requests.post(CURSE_HOST + url, json=data, timeout=60, headers=curse_login.get_headers())
        r.raise_for_status()
    except ConnectionError or requests.RequestException:
        r = requests.post(CURSE_HOST + url, json=data, timeout=60, headers=curse_login.get_headers())
        r.raise_for_status()
    return r


def get_routes_with_prefix(prefix, exclude=None):
    routes = []
    for rule in app.url_map.iter_rules():
        rule: werkzeug.routing.Rule = rule
        if not rule.endpoint.startswith(prefix):
            continue
        if exclude and rule.endpoint in exclude:
            continue
        routes.append({
            'name': rule.endpoint.replace(prefix, ''),
            'endpoint': rule.endpoint,
            'rule': rule,
            'function': app.view_functions[rule.endpoint]
        })
    return routes
