import json

import flask
import requests

app = flask.Flask(__name__)

HTML = r'''<!DOCTYPE html><html lang="en"><head> <meta charset="UTF-8"> <title>CurseMeta</title></head><body> <h1>CurseMeta</h1> 
<p>Admin/Coder/Webmaster/Postmaster: <a href="https://dries007.net">Dries007</a>.</p><p> This service is deprecated. You can now access the API directly. <a 
href="https://twitchappapi.docs.apiary.io">Documentation on that here.</a><br/> For help and information, join us on Discord: <a 
href="https://discord.gg/zCQaCAA">#cursemeta</a> Ask for private access if you need it, use the public channel otherwise. </p><p> This service is kept online 
because MultiMC relies on it for it's Twitch/CurseForge modpack installation.<br/> The only endpoint that is still maintained is 
<code>/{project_id}/{file_id}.json</code>. </p><p>Any contribution to the cost of keeping it online is greatly appreciated via <a 
href="https://www.patreon.com/dries007">Patreon</a> or <a href="https://paypal.me/dries007/5usd">PayPal</a>.</p><p> CurseMeta is not associated with 
Minecraft (and/or Mojang and/or Microsoft) and/or Curse (and/or Twitch and/or Amazon).<br/> This service is provided as medium to facilitate interoperability 
between the Curse mod database and third party tools. </p></body></html>'''
ROOT_URL = 'https://addons-ecs.forgesvc.net/api/v2/addon/'
ENUM = ['UNKNOWN', 'Folder', 'Ctoc', 'SingleFile', 'Cmod2', 'ModPack', 'Mod', ]


@app.route('/')
def index():
    return flask.render_template_string(HTML)


def _fix_names(obj):
    for key in list(obj.keys()):
        new_key = key[0].upper() + key[1:]
        new_key = new_key.replace('Url', 'URL')
        if new_key != key:
            obj[new_key] = obj[key]
            del obj[key]
    return obj


@app.route('/<int:project_id>/<int:file_id>.json')
def legacy(project_id: int, file_id: int):
    try:
        with open(str(file_id) + '.json') as f:
            return app.response_class(f.read(), mimetype=app.config['JSONIFY_MIMETYPE'])
    except:
        pass

    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'})
        r = session.get(ROOT_URL + str(project_id))
        r.raise_for_status()
        try:
            project_data = r.json(object_hook=_fix_names)
        except:
            return flask.jsonify({'status': 500, 'error': True, 'description': 'Project API request fail', 'api_response_body': r.text}), 500
        r = session.get(ROOT_URL + str(project_id) + '/file/' + str(file_id))
        r.raise_for_status()
        try:
            file_data = r.json(object_hook=_fix_names)
        except:
            return flask.jsonify({'status': 500, 'error': True, 'description': 'File API request fail', 'api_response_body': r.text}), 500

    file_data['FileNameOnDisk'] = file_data['FileName']
    file_data['__comment'] = 'Deprecated! [Served by AWS Lambda]'
    file_data['_Project'] = {'Path': project_data['CategorySection']['Path'], 'PackageType': ENUM[project_data['CategorySection']['PackageType']]}

    with open(str(file_id) + '.json', 'w') as f:
        json.dump(file_data, f)

    return flask.jsonify(file_data)

