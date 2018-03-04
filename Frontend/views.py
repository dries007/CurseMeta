import collections
import re
import json
import unicodedata

import flask
import logging
import markdown
import textwrap
import werkzeug.exceptions as exceptions

from . import app
from . import curse
from . import views_api_v2_direct
from .helpers import Documentation
from .helpers import to_json_response


ROOT_DOCS = collections.OrderedDict()
_LOGGER = logging.getLogger("Views")
_LOGGER.setLevel(logging.DEBUG)


@app.template_filter('tojson')
def filter_json(obj, indent=None) -> str or None:
    return None if obj is None else json.dumps(obj, indent=indent)


@app.template_filter('docstring')
def filter_docstring(obj) -> str or None:
    return None if obj.__doc__ is None else '\n'.join(x for x in textwrap.dedent(obj.__doc__).splitlines())


@app.template_filter('markdown')
def filter_markdown(md: str or None, header_base=1) -> str or None:
    extensions = ('markdown.extensions.nl2br', 'markdown.extensions.sane_lists', 'markdown.extensions.fenced_code', 'markdown.extensions.toc')
    extension_configs = {'markdown.extensions.toc':  {
        'baselevel': header_base,
        'slugify': lambda x, y: ''
    }}
    return None if md is None else flask.Markup(markdown.markdown(md, extensions=extensions, extension_configs=extension_configs, output_format='html5'))


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


@app.template_filter('slugify')
def slugify(text, delim='-'):
    return delim.join(filter(None, (unicodedata.normalize('NFKD', x) for x in _punct_re.split(text.lower()))))


@app.errorhandler(Exception)
def any_error(e: Exception):
    from jinja2 import TemplateNotFound
    if isinstance(e, TemplateNotFound):
        e = exceptions.NotFound()

    if not isinstance(e, exceptions.HTTPException):
        e = exceptions.InternalServerError()
        _LOGGER.exception("Error handler non HTTPException: %s", e)

    return flask.jsonify({'error': True, 'status': e.code, 'description': e.description}), e.code


@app.route('/<path:p>')
@app.route('/')
def page(p='index'):
    return flask.render_template('{}.html'.format(p))


@app.route('/docs')
def docs():
    apis = [
        ('Status API', None, ROOT_DOCS),
        ('Direct Curse Access', views_api_v2_direct.__doc__, views_api_v2_direct.DOCS),
    ]
    return flask.render_template('docs.html', apis=apis)


# todo: patch MultiMC to not use this endpoint
@app.route('/<int:addonID>/<int:fileID>.json')
def deprecated_project_file_json(addonID: int, fileID: int):
    return to_json_response(curse.service.GetAddOnFile(addonID=addonID, fileID=fileID))


ROOT_DOCS['Api root'] = Documentation(['GET /api/'], {}, {'status': 'string', 'message': 'string', 'apis': ['string']})
ROOT_DOCS['Api v2 direct'] = Documentation(['GET ' + views_api_v2_direct.URL_PREFIX], {}, {'status': 'string', 'message': 'string', 'apis': {'<Endpoint name>': {'inp': '<Input type>', 'outp': '<Output type>', 'rules': ['string']}}})


@app.route('/api/')
def api_root():
    return to_json_response({
        'status': 'OK',
        'message': None,
        'apis': [
            views_api_v2_direct.URL_PREFIX,
        ],
    })


@app.route(views_api_v2_direct.URL_PREFIX)
def api_v2_root():
    # noinspection PyProtectedMember
    return to_json_response({
        'status': 'OK',
        'message': None,
        'apis': {k: v._asdict() for k, v in views_api_v2_direct.DOCS.items()},
    })
