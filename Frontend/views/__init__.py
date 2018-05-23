import collections
import re
import json
import unicodedata

import flask
import logging
import textwrap
import requests
import werkzeug.exceptions as exceptions

from markdown import markdown

from .. import app
from .. import curse
from .. import curse_login
from ..helpers import Documentation
from ..helpers import to_json_response
from ..helpers import cache

# from . import api_v2_direct
# from . import api_v2_history
# from . import api_v2_stats


ROOT_DOCS = collections.OrderedDict()
_LOGGER = logging.getLogger("Views")
_LOGGER.setLevel(logging.DEBUG)
__SLUG_SPLIT_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

# ===== CONTEXT =====


@app.before_request
def before_request():
    pass

# ===== FILTERS =====


@app.template_filter('tojson')
def filter_json(obj, indent=None) -> str or None:
    return None if obj is None else json.dumps(obj, indent=indent)


@app.template_filter('docstring')
def filter_docstring(obj) -> str or None:
    return None if obj.__doc__ is None else '\n'.join(x for x in textwrap.dedent(obj.__doc__).splitlines())


@app.template_filter('markdown')
def filter_markdown(md: str or None, header_base=1, idprefix='md') -> str or None:
    if md is None:
        return None
    extensions = (
        'markdown.extensions.nl2br',  # \n to <br/>
        'markdown.extensions.sane_lists',  # Make lists behave more like GFmd
        'markdown.extensions.fenced_code',  # Add code fencing with ```
        'markdown.extensions.toc',  # Allow [toc], but also re-map header numbers
    )
    extension_configs = {
        'markdown.extensions.toc':  {
            'baselevel': header_base,  # Remap headers
            'slugify': lambda x, y: slugify(x, y, idprefix),  # Use same slugify as slugify filter
        },
    }
    return flask.Markup(markdown(md, extensions=extensions, extension_configs=extension_configs, output_format='html5'))


@app.template_filter('slugify')
def slugify(text, delimiter='-', prefix=None):
    split = (unicodedata.normalize('NFKD', x) for x in __SLUG_SPLIT_RE.split(text))
    return delimiter.join(filter(None, (prefix, *split))).lower()

# ===== ALL CASE ERROR HANDLER =====


@app.errorhandler(Exception)
def any_error(e: Exception):
    from jinja2 import TemplateNotFound
    if isinstance(e, TemplateNotFound):
        e = exceptions.NotFound()

    if not isinstance(e, exceptions.HTTPException):
        e = exceptions.InternalServerError()
        _LOGGER.exception("Error handler non HTTPException: %s", e)

    return flask.jsonify({'error': True, 'status': e.code, 'description': e.description}), e.code

# ===== NON - API ROUTES =====


@app.route('/<path:p>')
@app.route('/')
def page(p='index'):
    return flask.render_template('{}.html'.format(p))


@app.route('/docs')
def docs():
    apis = [
        ('API Status & Layout', None, ROOT_DOCS),
        # ('Direct Curse Access', api_v2_direct.__doc__, api_v2_direct.DOCS),
        # ('Historic data', api_v2_history.__doc__, api_v2_history.DOCS),
    ]
    return flask.render_template('docs.html', apis=apis)

# ===== API ROUTES =====


def _fix_names(obj):
    for key in obj.keys():
        new_key = key[0].upper() + key[1:]
        new_key = new_key.replace('Url', 'URL')
        if new_key != key:
            obj[new_key] = obj[key]
            del obj[key]
    return obj


# todo: patch MultiMC to not use this endpoint
# todo: maybe add user-agent check to make sure noone else still uses it?
@app.route('/<int:addonID>/<int:fileID>.json')
@cache()
def deprecated_project_file_json(addonID: int, fileID: int):
    data = requests.get('https://addons-v2.forgesvc.net/api/addon/%d/file/%d' % (addonID, fileID),
                        timeout=60,
                        headers={'AuthenticationToken': curse_login.get_token()}
                        ).json()
    return to_json_response(json.loads(json.dumps(data), object_hook=_fix_names))
    # token =
    # r = to_json_response(curse.service.GetAddOnFile(addonID=addonID, fileID=fileID))
    # r.headers.add('Warning', '299 - "Deprecated API"')
    # return r


ROOT_DOCS['API Status'] = Documentation(['GET /api/'], {}, {'status': 'string (OK = good)', 'message': 'string|None', 'apis': ['url']})


@app.route('/api/')
@cache(None)
def api_root():
    return to_json_response({
        'status': 'OK',
        'message': None,
        'apis': [
            # api_v2_direct.URL_PREFIX,
        ],
    })
