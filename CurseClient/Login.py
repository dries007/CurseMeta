import requests
import zeep
import lxml.etree as etree
import datetime
import json


def _post_json_retry(data, timeout=10, attempts=3):
    while attempts > 0:
        try:
            return requests.post('https://logins-v1.curseapp.net/login', json=data, timeout=timeout).json()
        except ConnectionError:
            attempts -= 1
            if attempts == 0:
                raise


class LoginClient(zeep.Plugin):
    def __init__(self, username, password, redis_store):
        self.redis = redis_store
        self.__username = username
        self.__password = password
        self.redis_key = 'CurseClientLogin-' + self.__username
        self.session = None
        if self.redis:
            # noinspection PyBroadException
            try:
                session = self.redis.get(self.redis_key) if self.redis else None
                self.session = json.loads(session) if session else None
            except BaseException:  # This is just in case the value got corrupted somehow
                self.redis.expire(self.redis_key, 0)
        self.renewAfter = datetime.datetime.fromtimestamp(self.session['RenewAfter'] / 1000) if self.session else None
        self.checklogin()

    def login(self):
        self.session = _post_json_retry({'Username': self.__username, 'Password': self.__password})['Session']
        self.renewAfter = datetime.datetime.fromtimestamp(self.session['RenewAfter'] / 1000)
        if self.redis:
            expire_sec = int((self.renewAfter - datetime.datetime.now()).total_seconds())
            self.redis.set(self.redis_key, json.dumps(self.session), ex=expire_sec)

    def checklogin(self):
        if self.session is None or self.renewAfter > datetime.datetime.now():
            self.login()
            return True
        return False

    def soap_token(self):
        self.checklogin()
        root = etree.Element('AuthenticationToken', xmlns='urn:Curse.FriendsService:v1')
        for k in ['Token', 'UserID']:
            tmp = etree.Element(k)
            tmp.text = str(self.session[k])
            root.append(tmp)
        return root

    def ingress(self, envelope, http_headers, operation):
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        envelope.find('{http://www.w3.org/2003/05/soap-envelope}Header').append(self.soap_token())
        return envelope, http_headers
