"""
History download counts

If you have cached data locally, don't just requires new data periodically.
Check the `timestamp` on the API Root to see if the data has been updated yet.

"""

import collections
import flask

import werkzeug.exceptions as exceptions

from .. import app
from .. import redis_store
from ..helpers import Documentation
from ..helpers import to_json_response
from ..helpers import cache

from ..tasks.history import get_dlfeed_key, FEEDS_INTERVALS

URL_PREFIX = '/api/v2/history'
DOCS = collections.OrderedDict()

DOCS['API Root'] = Documentation(['GET ' + URL_PREFIX],
                                 {},
                                 {'status': 'string (OK = good)',
                                  'message': 'string|null',
                                  'timestamp': 'int',
                                  'game_ids': ['int'],
                                  'intervals': ['string'],
                                  'apis': {'<Endpoint name>': {'inp': '<Input type>', 'outp': '<Output type>', 'rules': ['METHOD + template url'], 'extra': 'string|null'}}})
DOCS['Downloads'] = Documentation(['GET ' + URL_PREFIX + '/downloads/<int:game_id>/<string:interval>'],
                                  {'game_id': 'int', 'interval': 'string'},
                                  {'addon_id': 'long|float'},
                                  'If an addon_id is not present in this feed, it has not gotten any downloads.\n'
                                  'Assume data gathering started 2018-03-15. Data from before is inaccurate.')


@app.route(URL_PREFIX)
@cache(None)
def api_v2_history():
    timestamp = redis_store.get('history-timestamp')
    timestamp = int(timestamp) if timestamp is not None else None
    game_ids = list(sorted(int(x) for x in redis_store.smembers('history-game_ids')))

    # noinspection PyProtectedMember
    return to_json_response({
        'status': 'OK',
        'message': None,
        'timestamp': timestamp,
        'game_ids': game_ids,
        'intervals': list(FEEDS_INTERVALS.keys()),
        'apis': {k: v._asdict() for k, v in DOCS.items()}
    })


@app.route(URL_PREFIX + '/downloads/<int:game_id>/<string:interval>')
@cache(None)
def api_v2_history_downloads(game_id: int, interval: str):
    if game_id not in map(int, redis_store.smembers('history-game_ids')):
        raise exceptions.BadRequest('This gameid does not exist.')
    if interval not in FEEDS_INTERVALS:
        raise exceptions.BadRequest('This interval does not exist.')
    return flask.Response(redis_store.get(get_dlfeed_key(game_id, interval)), mimetype="application/json")
