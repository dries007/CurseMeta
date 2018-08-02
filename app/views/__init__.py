import re
import json
import unicodedata
import html2text

import flask
import werkzeug.routing
import logging
import textwrap
import requests
import werkzeug.exceptions as exceptions

from urllib.parse import unquote_plus as url_decode
from markdown import markdown
from sqlalchemy.sql.expression import func

from app.tasks import FEEDS_INTERVALS, get_dlfeed_key
from .. import app
from .. import curse_login
from .. import redis_store
from ..helpers import to_json_response
from ..helpers import cache
from ..helpers import get_curse_api
from ..helpers import post_curse_api
from ..helpers import get_routes_with_prefix
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
    return flask.render_template('index.html',
                                 max_addon=db.session.query(func.max(AddonModel.addon_id)).scalar(),
                                 max_file=db.session.query(func.max(FileModel.file_id)).scalar(),
                                 num_addons=db.session.query(AddonModel).count(),
                                 num_files=db.session.query(FileModel).count(),
                                 num_authors=db.session.query(AuthorModel).count(),
                                 num_history=db.session.query(HistoricRecord).count(),
                                 )


@app.route('/about')
def about():
    return flask.render_template('about.html')


@app.route('/docs')
def docs():
    exclude = set()

    v3_history = get_routes_with_prefix('api_v3_history', exclude)
    exclude.update(x['endpoint'] for x in v3_history)

    v3_direct = get_routes_with_prefix('api_v3_direct', exclude)
    exclude.update(x['endpoint'] for x in v3_direct)

    v3 = get_routes_with_prefix('api_v3', exclude)
    exclude.update(x['endpoint'] for x in v3)

    leftover = get_routes_with_prefix('api', exclude)

    return flask.render_template('docs.html',
                                 v3=v3,
                                 v3_direct=v3_direct,
                                 v3_history=v3_history,
                                 leftover=leftover
                                 )


@app.route('/api/<path:p>')
def missing_api(p):
    raise exceptions.NotFound('API url not found: \'%s\'. For a list, see the documentation on the main site.' % p)


# ===== General 1:1 API mapping =====


# ----- Addons -----

@app.route('/api/v3/direct/addon/<int:addon_id>')
@cache()
def api_v3_direct_get_addon(addon_id: int):
    """
    See _Get Addons_ to request multiple addons at once.
    Required:
    - `addon_id`: A single addon ID
    """
    data = get_curse_api('api/addon/%d' % addon_id).json()
    AddonModel.update(data)
    return to_json_response(data)


@app.route('/api/v3/direct/addon')
@cache()
def api_v3_direct_get_addons():
    """
    Required:
    - GET `id`: One or more addon ids. Just specify more than once.
    """
    data = post_curse_api('api/addon', flask.request.args.getlist('id', type=int)).json()
    for x in data:
        AddonModel.update(x)
    return to_json_response(data)


@app.route('/api/v3/direct/addon/search')
@cache()
def api_v3_direct_get_search():
    """
    Required:
    - GET: `gameId`: Which game to search
    Optional:
    - TODO: add optional parameters to docs, see http://ix.io/1bll/C#, line nr 47
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
    See _Get Addons Files_ to request multiple pairs at once.
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


@app.route('/api/v3/direct/addon/files')
@cache()
def api_v3_direct_get_addons_files():
    """
    You **must** have an equal number of `addon` and `file` parameters.

    Required:
    - GET `addon`: One or more addon ids. Just specify more than once.
    - GET `file`: One or more file ids. Just specify more than once.
    """
    addons = flask.request.args.getlist('addon', type=int)
    files = flask.request.args.getlist('file', type=int)

    if len(addons) != len(files):
        raise exceptions.BadRequest('len(addons) != len(files)')

    data = [{'addonId': addon, 'fileId': file} for addon, file in zip(addons, files)]
    data = post_curse_api('api/addon/files', data).json()
    for addon_id, x in data.items():
        for xx in x:
            FileModel.update(addon_id, xx)
    return to_json_response(data)


@app.route('/api/v3/direct/addon/slug')
@cache()
def api_v3_direct_get_repo_from_slug():
    """
    Might have something to do with WOW, git/hg repos. _Requires further research._
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
    data = post_curse_api('api/addon/featured', {
        'GameId': flask.request.args.get('gameId', type=int),
        'FeaturedCount': flask.request.args.get('featuredCount', 6, type=int),
        'PopularCount': flask.request.args.get('popularCount', 14, type=int),
        'UpdatedCount': flask.request.args.get('updatedCount', 14, type=int),
        'ExcludedAddons': flask.request.args.getlist('addonIds', type=int),
    }).json()
    for k, v in data.items():
        AddonModel.update(v)
    return to_json_response(data)


@app.route('/api/v3/direct/addon/timestamp')
@cache()
def api_v3_direct_get_timestamp():
    """
    Get the last (Curse internal) update timestamp
    """
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
    """
    todo: how does this work? it's the same url and endpoint as `api_v3_direct_get_mc_modloader_by_key`...
    """
    return to_json_response(get_curse_api('api/minecraft/modloader/%s' % key).json())


@app.route('/api/v3/direct/minecraft/modloader/timestamp')
@cache()
def api_v3_direct_get_mc_modloader_timestamp():
    """
    Get the last (Curse internal) update timestamp
    """
    return get_curse_api('api/minecraft/modloader/timestamp').text


# ----- MC Versions -----

@app.route('/api/v3/direct/minecraft/version')
@cache()
def api_v3_direct_get_mc_versions():
    return to_json_response(get_curse_api('api/minecraft/version').json())


@app.route('/api/v3/direct/minecraft/version/timestamp')
@cache()
def api_v3_direct_get_mc_version_timestamp():
    """
    Get the last (Curse internal) update timestamp
    """
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
    """
    Get the last (Curse internal) update timestamp
    """
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
    """
    Get the last (Curse internal) update timestamp
    """
    return get_curse_api('api/category/timestamp').text


# ===== Manifest.json =====


@app.route('/api/v3/manifest', methods=['POST'])
@cache(None)
def api_v3_manifest():
    """
    Upload a manifest.json from a Curse/Twitch modpack and it will be returned
    with the list of files replaced with the projectID-fileID pairs resolved.

    The resolved file data will be inserted in an added data field called `fileData`.
    Any unsolvable files will remain, with an added data field `fileError`.

    Required:
    - POST: json manifest from Minecraft Modpack, version 1 only.

    Optional:
    - GET: `resolveAddons`: Also resolve and add addon data to field called `addonData`.
    """
    manifest = flask.request.get_json(force=True)
    if manifest is None:
        raise exceptions.BadRequest('Data was not json.')
    if manifest['manifestType'] != 'minecraftModpack':
        raise exceptions.BadRequest('Unknown manifest type.')
    if manifest['manifestVersion'] != 1:
        raise exceptions.BadRequest('Unknown manifest version.')

    files = manifest['files']

    file_data = [{'addonId': x['projectID'], 'fileId': x['fileID']} for x in files]
    file_data = post_curse_api('api/addon/files', file_data).json()
    for addon_id, x in file_data.items():
        for xx in x:
            FileModel.update(addon_id, xx)

    if 'resolveAddons' in flask.request.args:
        addon_data = {x['id']: x for x in post_curse_api('api/addon', [x['projectID'] for x in files]).json()}
        for x in addon_data.values():
            AddonModel.update(x)
    else:
        addon_data = None

    for file in files:
        for x in file_data[str(file['projectID'])]:
            if file['fileID'] == x['id']:
                file['fileData'] = x
                break
        if 'fileData' not in file:
            file['fileError'] = True
        if addon_data:
            if file['projectID'] in addon_data:
                file['addonData'] = addon_data[file['projectID']]
            else:
                file['addonError'] = True

    return to_json_response(manifest)


# ===== Historical data =====


@app.route('/api/v3/history/feeds')
@cache(None)
def api_v3_history_feeds():
    """
    Get a list of which feeds are available.
    They are periodically generated and updated.
    The returned timestamp is when the generation last took place. If that's null, there has been none.
    """
    timestamp = redis_store.get('history-timestamp')
    timestamp = int(timestamp) if timestamp is not None else None
    game_ids = list(sorted(int(x) for x in redis_store.smembers('history-game_ids')))

    # noinspection PyProtectedMember
    return to_json_response({
        'timestamp': timestamp,
        'game_ids': game_ids,
        'intervals': FEEDS_INTERVALS
    })


@app.route('/api/v3/history/downloads/<int:game_id>/<string:interval>')
@cache(None)
def api_v3_history_downloads(game_id: int, interval: str):
    """
    Get a list of download numbers in the last `interval`.
    A list of intervals generated is provided via the _Feeds_ endpoint.

    The output is a map of `addon ids` → `download delta`. A negative delta is possible.
    """
    if game_id not in map(int, redis_store.smembers('history-game_ids')):
        raise exceptions.BadRequest('This gameid does not exist or there is no feed yet.')
    if interval not in FEEDS_INTERVALS:
        raise exceptions.BadRequest('This interval does not exist or there is no feed yet.')
    return flask.Response(redis_store.get(get_dlfeed_key(game_id, interval)), mimetype="application/json")


# ===== DB access =====


@app.route('/api/v0/db/slug', methods=['GET', 'POST'])
@cache()
def api_v0_db_slug():
    """
    Required:
    - GET: `slug`: The slug to look up. Can be specified multiple times.

    A null value or missing key means no data was found.

    **WARNING** Provisional API. Don't use in client side projects.
    """

    if flask.request.method == 'POST':
        slugs = flask.request.get_json(force=True)
    else:
        slugs = flask.request.args.getlist('slug', type=str)
    addons = AddonModel.query.filter(AddonModel.slug.in_(slugs)).all()
    return to_json_response({
        addon.slug: {
            'id': addon.addon_id,
            'last_update': int(addon.last_update.timestamp()),
            'game': addon.game_id,
            'name': addon.name,
            'category': addon.category,
            'downloads': addon.downloads,
            'score': addon.score,
        } for addon in addons
    })


@app.route('/api/v0/db/dump', methods=['GET', 'POST'])
@cache()
def api_v0_db_dump():
    """
    Dumps the whole (addon) DB.
    Some members may be null.

    **WARING**: Large!

    Optional:
    - GET: `files`: Also dump the whole file DB. (**WARING**: Extra Large!)
    - GET: `game`: Filter based on game. Can be specified multiple times.

    **WARNING** Provisional API. Don't use in client side projects.
    """
    games = flask.request.args.getlist('game', type=str)
    if games:
        addons = AddonModel.query.filter(AddonModel.game_id.in_(games)).all()
    else:
        addons = AddonModel.query.all()

    files = 'files' in flask.request.args
    return to_json_response([
        {
            'id': addon.addon_id,
            'last_update': int(addon.last_update.timestamp()),
            'slug': addon.slug,
            'game': addon.game_id,
            'name': addon.name,
            'category': addon.category,
            'downloads': addon.downloads,
            'score': addon.score,
            'files': None if not files else [
                {
                    'id': file.file_id,
                    'last_update': int(file.last_update.timestamp()),
                    'name': file.name,
                    'url': file.url,
                } for file in addon.files
            ]
        } for addon in addons
    ])


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
def api_deprecated_project_file_json(addon_id: int, file_id: int):
    """
    **DEPRECATED**
    """
    enum = [
        'UNKNOWN',
        'Folder',
        'Ctoc',
        'SingleFile',
        'Cmod2',
        'ModPack',
        'Mod',
    ]
    file_data = get_curse_api('api/addon/%d/file/%d' % (addon_id, file_id)).json(object_hook=_fix_names)
    project_data = get_curse_api('api/addon/%d' % addon_id).json(object_hook=_fix_names)
    print(file_data)
    print(project_data)
    file_data['__comment'] = 'WARNING: Deprecated API, Should only be used by existing users.'
    file_data['_Project'] = {
        'Path': project_data['CategorySection']['Path'],
        'PackageType': enum[project_data['PackageType']]
    }
    r = to_json_response(file_data)
    r.headers.add('Warning', '299 - "Deprecated API"')
    FileModel.update_old(addon_id, file_data)
    return r
