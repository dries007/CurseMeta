import os
import json

GOOGLE_ANALYTICS = '115047102-1'
PREFERRED_URL_SCHEME = 'https'
CACHE_TYPE = 'redis'
SQLALCHEMY_TRACK_MODIFICATIONS = False

STAGING = os.environ.get('FLASK_ENV', None) == 'staging'
DEVELOPMENT = os.environ.get('FLASK_ENV', None) == 'development'

LOGGER_NAME = 'CurseMeta'
TEMPLATES_AUTO_RELOAD = False
DEBUG = False
JSONIFY_PRETTYPRINT_REGULAR = False
CELERY_BROKER_URL = CELERY_RESULT_BACKEND = 'redis+socket:///run/redis/redis.sock?virtual_host=3'
REDIS_URL = 'unix:///run/redis/redis.sock?db=3'


def get_file(name):
    for filename in [name, 'run/' + name, os.path.expanduser('~/' + name)]:
        if os.path.isfile(filename):
            return filename
    return None


db_user = 'cursemeta'
db_host = 'localhost'
db_port = 5432
db_name = db_user
f = get_file('db.pwd')
if f is not None:
    with open(f, 'r') as f:
        db_pwd = f.read().strip()
else:
    db_pwd = None

if STAGING or DEVELOPMENT:
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = True
    FLASK_DEBUG = True
    JSONIFY_PRETTYPRINT_REGULAR = True

if STAGING:
    LOGGER_NAME += '_Staging'
    CELERY_BROKER_URL = CELERY_RESULT_BACKEND = CELERY_BROKER_URL[:-1] + '4'
    REDIS_URL = REDIS_URL[:-1] + '4'
    db_name += '_staging'

if DEVELOPMENT:
    LOGGER_NAME += '_Dev'
    CELERY_BROKER_URL = CELERY_RESULT_BACKEND = CELERY_BROKER_URL[:-1] + '5'
    REDIS_URL = REDIS_URL[:-1] + '5'
    db_name += '_dev'

if db_pwd:
    SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@%s:%d/%s' % (db_user, db_pwd, db_host, db_port, db_name)
else:
    SQLALCHEMY_DATABASE_URI = 'postgresql://%s@%s:%d/%s' % (db_user, db_host, db_port, db_name)
print(SQLALCHEMY_DATABASE_URI)
del db_user, db_pwd, db_host, db_port, db_name


def get_git_hash(*args):
    import subprocess
    try:
        return subprocess.check_output(('git', 'rev-parse', *args, 'HEAD'), stderr=subprocess.STDOUT).strip().decode()
    except subprocess.CalledProcessError:
        return None


SHORT_COMMIT_HASH = get_git_hash('--short')
LONG_COMMIT_HASH = get_git_hash()
print("Git commit:", SHORT_COMMIT_HASH, LONG_COMMIT_HASH)

f = get_file('secret-key.bin')
if f:
    with open(f, 'rb') as f:
        SECRET_KEY = f.read().strip()
else:
    print("Using temp secret key, sessions won't persist, make a static one!")
    SECRET_KEY = os.urandom(512)

with open(get_file('curse.txt'), 'r') as f:
    CURSE_CODE = f.read().strip()

with open(get_file('ifttt.txt'), 'r') as f:
    IFTTT_CODE = f.read().strip()
