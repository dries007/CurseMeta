import os

GOOGLE_ANALYTICS = '115047102-1'
SOAP_CACHE = 3600
PREFERRED_URL_SCHEME = 'https'
STAGING = False

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

if 'CONFIG_ENV' in os.environ and os.environ['CONFIG_ENV'] == 'staging':
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = True
    SOAP_CACHE = None
    STAGING = True

del os
