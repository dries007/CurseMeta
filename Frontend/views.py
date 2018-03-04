import flask
import logging
import werkzeug.exceptions as exceptions

from . import app
from . import curse
from . import views_api_v2_direct
from .helpers import to_json_response


_LOGGER = logging.getLogger("Views")
_LOGGER.setLevel(logging.DEBUG)


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
    return flask.render_template('docs.html', endpoints=views_api_v2_direct.DOCS)


# todo: patch MultiMC to not use this endpoint
@app.route('/<int:addonID>/<int:fileID>.json')
def deprecated_project_file_json(addonID: int, fileID: int):
    return to_json_response(curse.service.GetAddOnFile(addonID=addonID, fileID=fileID))


@app.route('/api/')
def api_root():
    return to_json_response({
        'status': 'OK',
        'message': None,
        'apis': [
            views_api_v2_direct.URL_PREFIX,
        ],
    })
