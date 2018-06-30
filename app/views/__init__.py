import re
import json
import unicodedata
import html2text
from urllib.parse import unquote_plus as url_decode

import flask
import werkzeug.routing
import logging
import textwrap
import requests
import werkzeug.exceptions as exceptions

from markdown import markdown

from .. import app
from .. import curse_login
from ..helpers import to_json_response
from ..helpers import cache
from ..helpers import get_curse_api
from ..helpers import CURSE_HOST
from ..models import *


_LOGGER = logging.getLogger('Views')
_LOGGER.setLevel(logging.DEBUG)
__SLUG_SPLIT_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
__LINK_FIX_RE = re.compile(r'href="/linkout\?remoteUrl=([\w%.]+)"')

html2text.config.PAD_TABLES = True
html2text.config.USE_AUTOMATIC_LINKS = False

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
        e = exceptions.NotFound("Template(s) not found: " + str(e))

    if not isinstance(e, exceptions.HTTPException):
        e = exceptions.InternalServerError(str(e))
        _LOGGER.exception("Error handler non HTTPException: %s", e)

    return flask.jsonify({'error': True, 'status': e.code, 'description': e.description}), e.code

# ===== NON - API ROUTES =====


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/about')
def about():
    return flask.render_template('about.html')


@app.route('/docs')
def docs():
    apis = []
    for rule in app.url_map.iter_rules():
        rule: werkzeug.routing.Rule
        if not rule.endpoint.startswith('api_v3_'):
            continue
        apis.append({
            'name': rule.endpoint.replace('api_v3_', ''),
            'rule': rule,
            'function': app.view_functions[rule.endpoint]
        })
    return flask.render_template('docs.html', apis=apis)


@app.route('/api/<path:p>')
def missing_api(p):
    raise exceptions.NotFound('API url not found: \'%s\'. For a list, see the documentation on the main site.' % p)


# ===== General 1:1 API mapping =====


# ----- Addons -----

@app.route('/api/v3/direct/addon/<int:addon_id>')
@cache()
def api_v3_direct_get_addon(addon_id: int):
    """
    Required:
    - `addon_id`: A single addon ID
    """
    data = get_curse_api('api/addon/%d' % addon_id).json()
    AddonModel.update(data)
    return to_json_response(data)


# todo: Add POST(?) for multiple addons at the same time. (maybe just allow a GET with multiple 'addonId' parameters?)

@app.route('/api/v3/direct/addon/search')
@cache()
def api_v3_direct_get_search():
    """
    Required:
    - GET: `gameId`: Which game to search
    Optional:
    - TODO: add optional parameters to docs, see http://ix.io/1bll/C#
    """
    data = get_curse_api('api/addon/search', flask.request.args).json()
    for x in data:
        AddonModel.update(x)
    return to_json_response(data)


@app.route('/api/v3/direct/addon/<int:addon_id>/description')
@cache()
def api_v3_direct_get_addon_description(addon_id: int):
    """
    Required:
    - `addon_id`: A single addon ID
    Optional:
    - GET: `markdown` or `md`: If present, converts html to markdown. Might not be accurate.
    - GET: `fixlinks`: If present, replace `/linkout?=<url>` with the actual direct url.
    Return type: HTML!
    """
    data = get_curse_api('api/addon/%d/description' % addon_id).text
    if 'fixlinks' in flask.request.args:
        data = re.sub(__LINK_FIX_RE, lambda x: 'href="%s"' % url_decode(url_decode(x.group(1))), data)
    if 'md' in flask.request.args or 'markdown' in flask.request.args:
        data = html2text.html2text(data, 'https://www.curseforge.com', 0)
    return data


@app.route('/api/v3/direct/addon/<int:addon_id>/file/<int:file_id>/changelog')
@cache()
def api_v3_direct_get_addon_changelog(addon_id: int, file_id: int):
    """
    Required:
    - `addon_id`: A single addon ID
    - `file_id`: A single file ID
    Optional:
    - GET: `markdown` or `md`: If present, converts html to markdown. Might not be accurate.
    - GET: `fixlinks`: If present, replace `/linkout?=<url>` with the actual direct url.
    Return type: HTML!
    """
    data = get_curse_api('api/addon/%d/file/%d/changelog' % (addon_id, file_id)).text
    if 'fixlinks' in flask.request.args:
        data = re.sub(__LINK_FIX_RE, lambda x: 'href="%s"' % url_decode(url_decode(x.group(1))), data)
    if 'md' in flask.request.args or 'markdown' in flask.request.args:
        data = html2text.html2text(data, 'https://www.curseforge.com', 0)
    return data


@app.route('/api/v3/direct/addon/<int:addon_id>/file/<int:file_id>')
@cache()
def api_v3_direct_get_addon_file(addon_id: int, file_id: int):
    """
    Required:
    - `addon_id`: A single addon ID
    - `file_id`: A single file ID
    """
    data = get_curse_api('api/addon/%d/file/%d' % (addon_id, file_id)).json()
    FileModel.update(addon_id, data)
    return to_json_response(data)


@app.route('/api/v3/direct/addon/<int:addon_id>/files')
@cache()
def api_v3_direct_get_addon_files(addon_id: int):
    """
    Required:
    - `addon_id`: A single addon ID
    """
    data = get_curse_api('api/addon/%d/files' % addon_id).json()
    for x in data:
        FileModel.update(addon_id, x)
    return to_json_response(data)

# todo: Add POST(?) endpoint for 'api/addon/files' This is based on 'AddonFileKey's


@app.route('/api/v3/direct/addon/slug')
@cache()
def api_v3_direct_get_repo_from_slug():
    """
    Might have something to do with WOW, git/hg repos. Requires further research.
    Required:
    - GET `gameSlug`: A string. todo: find out what this means
    - GET `addonSlug`: A string. todo: find out what this means
    """
    return to_json_response(get_curse_api('api/addon/slug', flask.request.args).json())


@app.route('/api/v3/direct/addon/featured')
@cache()
def api_v3_direct_get_featured():
    """
    Required:
    - GET: `gameId`: Which game to search
    Optional:
    - GET: `featuredCount`: Defaults to 6
    - GET: `popularCount`: Defaults to 14
    - GET: `updatedCount`: Defaults to 14
    - GET: `excluded`: Exclude an addon ID. Can be specified multiple times.
    """
    # todo: cache in redis?
    r = requests.post(CURSE_HOST + 'api/addon/featured', json={
        'GameId': flask.request.args.get('gameId'),
        'FeaturedCount': flask.request.args.get('featuredCount', 6),
        'PopularCount': flask.request.args.get('popularCount', 14),
        'UpdatedCount': flask.request.args.get('updatedCount', 14),
        'ExcludedAddons': flask.request.args.getlist('addonIds'),
    }, timeout=60, headers=curse_login.get_headers())
    r.raise_for_status()
    data = r.json()
    for k, v in data.items():
        AddonModel.update(v)
    return to_json_response(data)


@app.route('/api/v3/direct/addon/timestamp')
@cache()
def api_v3_direct_get_timestamp():
    return get_curse_api('api/addon/timestamp').text


# ----- MC Modloaders -----

@app.route('/api/v3/direct/minecraft/modloader')
@cache()
def api_v3_direct_get_mc_modloader():
    return to_json_response(get_curse_api('api/minecraft/modloader').json())


@app.route('/api/v3/direct/minecraft/modloader/<string:key>')
@cache()
def api_v3_direct_get_mc_modloader_by_key(key: str):
    return to_json_response(get_curse_api('api/minecraft/modloader/%s' % key).json())


@app.route('/api/v3/direct/minecraft/modloader/<string:key>')
@cache()
def api_v3_direct_get_mc_modloader_by_version(key: str):
    # todo: how does this work? it's the same url and endpoint.
    return to_json_response(get_curse_api('api/minecraft/modloader/%s' % key).json())


@app.route('/api/v3/direct/minecraft/modloader/timestamp')
@cache()
def api_v3_direct_get_mc_modloader_timestamp():
    return get_curse_api('api/minecraft/modloader/timestamp').text


# ----- MC Versions -----

@app.route('/api/v3/direct/minecraft/version')
@cache()
def api_v3_direct_get_mc_versions():
    return to_json_response(get_curse_api('api/minecraft/version').json())


@app.route('/api/v3/direct/minecraft/version/timestamp')
@cache()
def api_v3_direct_get_mc_version_timestamp():
    return get_curse_api('api/minecraft/version/timestamp').text


@app.route('/api/v3/direct/minecraft/version/<string:game_version>')
@cache()
def api_v3_direct_get_mc_version(game_version: str):
    return to_json_response(get_curse_api('api/minecraft/version/%s' % game_version).json())


# ----- Games -----

@app.route('/api/v3/direct/game')
@cache()
def api_v3_direct_get_games():
    """
    Optional:
    - GET `supportsAddons`: Defaults to False.
    """
    return to_json_response(get_curse_api('api/game', flask.request.args).json())


@app.route('/api/v3/direct/game/<int:game_id>')
@cache()
def api_v3_direct_get_game(game_id: int):
    """
    Required:
    - `game_id`: A single game id.
    """
    return to_json_response(get_curse_api('api/game/%d' % game_id).json())


@app.route('/api/v3/direct/game/timestamp')
@cache()
def api_v3_direct_get_game_timestamp():
    return get_curse_api('api/game/timestamp').text


# ----- Categories -----


@app.route('/api/v3/direct/category')
@cache()
def api_v3_direct_get_categories():
    """
    Optional:
    - GET `slug`: Search by slug
    """
    return to_json_response(get_curse_api('api/category', flask.request.args).json())


@app.route('/api/v3/direct/category/<int:category_id>')
@cache()
def api_v3_direct_get_category(category_id: int):
    """
    Required:
    - `category_id`: A single category id.
    """
    return to_json_response(get_curse_api('api/category/%d' % category_id).json())


@app.route('/api/v3/direct/category/section/<int:section_id>')
@cache()
def api_v3_direct_get_category_by_section(section_id: int):
    """
    Required:
    - `section_id`: A single section id. Idk where to get these from.
    """
    return to_json_response(get_curse_api('api/category/section/%d' % section_id).json())


@app.route('/api/v3/direct/category/timestamp')
@cache()
def api_v3_direct_get_category_timestamp():
    return get_curse_api('api/category/timestamp').text

# ===== MultiMC =====


def _fix_names(obj):
    for key in obj.keys():
        new_key = key[0].upper() + key[1:]
        new_key = new_key.replace('Url', 'URL')
        if new_key != key:
            obj[new_key] = obj[key]
            del obj[key]
    return obj


@app.route('/<int:addon_id>/<int:file_id>.json')
@cache()
def deprecated_project_file_json(addon_id: int, file_id: int):
    data = get_curse_api('api/addon/%d/file/%d' % (addon_id, file_id)).json(object_hook=_fix_names)
    data['__comment'] = 'WARNING: Deprecated API, Should only be used by existing users.'
    r = to_json_response(data)
    r.headers.add('Warning', '299 - "Deprecated API"')
    FileModel.update_old(addon_id, data)
    return r
