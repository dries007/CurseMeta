import requests
import zeep
import lxml.etree as etree


_URL = 'https://logins-v1.curseapp.net/login'


class LoginClient(zeep.Plugin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = None

    def auth(self):
        resp = requests.post(_URL, json={'Username': self.username, 'Password': self.password})
        json = resp.json()
        self.session = json['Session']

    def soap_token(self):
        if self.session is None:
            self.auth()
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
