TEMPLATES_AUTO_RELOAD = True
GOOGLE_ANALYTICS = "115047102-1"
SOAP_CACHE = 3600

with open('account.json', 'r') as f:
    import json
    t = json.load(f)
    CURSE_USER = t['Username']
    CURSE_PASS = t['Password']
    del t
