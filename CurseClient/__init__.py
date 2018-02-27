import zeep
import lxml.etree as etree
import json

from . import Login

# DEBUG = True
#
#
# def pprint(e: etree.Element, *args, **kwargs):
#     if len(args) != 0:
#         print(*args, **kwargs)
#     print(etree.tostring(e, pretty_print=True).decode('ascii'))
#

with open('account.json', 'r') as f:
    account = json.load(f)
    login = Login.LoginClient(account['username'], account['password'])
    login.auth()

c = zeep.Client(wsdl='https://addons.forgesvc.net/AddOnService.svc?singleWsdl', plugins=[login])
s = c.bind('AddOnService', 'WsHttpAddOnServiceEndpoint')

#
# c = zeep.Client(wsdl='https://addons.forgesvc.net/AddOnService.svc?singleWsdl', plugins=[CurseAuthZeepPlugin()])
# # c.raw_response = True
# # s_bin = c.bind('AddOnService', 'BinaryHttpAddOnServiceEndpoint')
# s = c.bind('AddOnService', 'WsHttpAddOnServiceEndpoint')
#
#
# print(s.HealthCheck())
# print(s.ListFeeds())
