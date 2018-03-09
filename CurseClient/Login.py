import requests
import zeep
import lxml.etree as etree
import datetime


def post_json_retry(json, timeout=30, attempts=3):
    while attempts > 0:
        try:
            return requests.post('https://logins-v1.curseapp.net/login', json=json, timeout=timeout).json()
        except ConnectionError:
            attempts -= 1
            if attempts == 0:
                raise


class LoginClient(zeep.Plugin):
    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.session = None
        self.renewAfter = None

    def login(self):
        self.session = post_json_retry({'Username': self.__username, 'Password': self.__password})['Session']
        self.renewAfter = datetime.datetime.fromtimestamp(self.session['RenewAfter'] / 1000)

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
