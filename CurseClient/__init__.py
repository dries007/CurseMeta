import zeep
import lxml.etree as etree
import json

from .Login import LoginClient


class CurseClient:
    def __init__(self, username, password):
        self.__login = LoginClient(username, password)
        self.__zeep_client = zeep.Client(wsdl='https://addons.forgesvc.net/AddOnService.svc?singleWsdl', plugins=[self.__login])
        self.__service = self.__zeep_client.bind('AddOnService', 'WsHttpAddOnServiceEndpoint')

    @classmethod
    def from_file(cls, file='account.json'):
        with open(file, 'r') as f:
            account = json.load(f)
            return cls(account['Username'], account['Password'])

    def list_functions(self):
        return filter(lambda x: not x.startswith('_'), dir(self))

    def debug(self):
        print('Debug CurseClient')
        print('  List of services:', *self.list_functions(), sep='\n   - ')

    def __getattr__(self, key):
        return self.__service.__getattr__(key)

    def __getitem__(self, key):
        return self.__service.__getitem__(key)

    def __dir__(self):
        return self.__service.__dir__()


# DEBUG = True
#
#
# def pprint(e: etree.Element, *args, **kwargs):
#     if len(args) != 0:
#         print(*args, **kwargs)
#     print(etree.tostring(e, pretty_print=True).decode('ascii'))
#
#
# with open('account.json', 'r') as f:
#     account = json.load(f)
#     login = Login.LoginClient(account['username'], account['password'])
#     login.auth()
#
# c = zeep.Client(wsdl='https://addons.forgesvc.net/AddOnService.svc?singleWsdl', plugins=[login])
# s = c.bind('AddOnService', 'WsHttpAddOnServiceEndpoint')

#
# c = zeep.Client(wsdl='https://addons.forgesvc.net/AddOnService.svc?singleWsdl', plugins=[CurseAuthZeepPlugin()])
# # c.raw_response = True
# # s_bin = c.bind('AddOnService', 'BinaryHttpAddOnServiceEndpoint')
# s = c.bind('AddOnService', 'WsHttpAddOnServiceEndpoint')
#
#
# print(s.HealthCheck())
# print(s.ListFeeds())
