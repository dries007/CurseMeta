import os

GOOGLE_ANALYTICS = '115047102-1'
SOAP_CACHE = 3600
PREFERRED_URL_SCHEME = 'https'
STAGING = False
LOGGER_NAME = 'Flask'
SHORT_COMMIT_HASH = None
LONG_COMMIT_HASH = None
JSONIFY_PRETTYPRINT_REGULAR = False


try:
    import subprocess
    SHORT_COMMIT_HASH = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode()
    LONG_COMMIT_HASH = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode()
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

if os.environ.get('CONFIG_ENV', None) == 'staging':
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = True
    SOAP_CACHE = None
    STAGING = True
    JSONIFY_PRETTYPRINT_REGULAR = True

del os
