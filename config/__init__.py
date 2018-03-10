GOOGLE_ANALYTICS = '115047102-1'
PREFERRED_URL_SCHEME = 'https'
LOGGER_NAME = 'Flask'
CACHE_TYPE = 'redis'

import os
STAGING = os.environ.get('CONFIG_ENV', None) == 'staging'
del os

TEMPLATES_AUTO_RELOAD = False if not STAGING else True
DEBUG = False if not STAGING else True
JSONIFY_PRETTYPRINT_REGULAR = False if not STAGING else True
SOAP_CACHE = 3600 if not STAGING else None
CELERY_BROKER_URL = CELERY_RESULT_BACKEND = 'redis+socket:///run/redis/redis.sock?virtual_host={}'.format(1 if not STAGING else 2)
REDIS_URL = 'unix:///run/redis/redis.sock?db={}'.format(1 if not STAGING else 2)

SHORT_COMMIT_HASH = None
LONG_COMMIT_HASH = None
try:
    import subprocess

    def _exec(*args):
        return subprocess.check_output(args, stderr=subprocess.STDOUT).strip().decode()

    SHORT_COMMIT_HASH = _exec('git', 'rev-parse', '--short', 'HEAD')
    LONG_COMMIT_HASH = _exec('git', 'rev-parse', 'HEAD')
    print("Git commit:", SHORT_COMMIT_HASH, LONG_COMMIT_HASH)
except subprocess.CalledProcessError:
    pass

try:
    with open('secret-key.bin', 'rb') as f:
        SECRET_KEY = f.read()
except FileNotFoundError:
    SECRET_KEY = os.urandom(512)
    with open('secret-key.bin', 'wb') as f:
        f.write(SECRET_KEY)

with open('account.json', 'r') as f:
    import json
    t = json.load(f)
    CURSE_USER = t['Username']
    CURSE_PASS = t['Password']
    del t
