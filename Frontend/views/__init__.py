import collections
import re
import json
import unicodedata

import flask
import logging
import textwrap
import werkzeug.exceptions as exceptions

from markdown import markdown

from .. import app
from .. import curse
from ..helpers import Documentation
from ..helpers import to_json_response
from ..helpers import cache

from . import api_v2_direct


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
        ('Status API', None, ROOT_DOCS),
        ('Direct Curse Access', api_v2_direct.__doc__, api_v2_direct.DOCS),
    ]
    return flask.render_template('docs.html', apis=apis)

# ===== API ROUTES =====


# todo: patch MultiMC to not use this endpoint
# todo: maybe add user-agent check to make sure noone else still uses it?
@app.route('/<int:addonID>/<int:fileID>.json')
@cache()
def deprecated_project_file_json(addonID: int, fileID: int):
    r = to_json_response(curse.service.GetAddOnFile(addonID=addonID, fileID=fileID))
    r.headers.add('Warning', '299 - "Deprecated API"')
    return r


ROOT_DOCS['Api root'] = Documentation(['GET /api/'], {}, {'status': 'string', 'message': 'string', 'apis': ['string']})


@app.route('/api/')
@cache(None)
def api_root():
    return to_json_response({
        'status': 'OK',
        'message': None,
        'apis': [
            api_v2_direct.URL_PREFIX,
        ],
    })


ROOT_DOCS['Api v2 direct'] = Documentation(['GET ' + api_v2_direct.URL_PREFIX], {}, {'status': 'string', 'message': 'string', 'apis': {'<Endpoint name>': {'inp': '<Input type>', 'outp': '<Output type>', 'rules': ['string']}}})


@app.route(api_v2_direct.URL_PREFIX)
@cache(None)
def api_v2_root():
    # noinspection PyProtectedMember
    return to_json_response({
        'status': 'OK',
        'message': None,
        'apis': {k: v._asdict() for k, v in api_v2_direct.DOCS.items()},
    })
