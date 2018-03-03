import zeep
import zeep.cache
import json

from .Login import LoginClient
from .OperationWrapper import OperationWrapper


class CurseClient:
    """
    Curse SOAP API client
    """
    def __init__(self, username, password, cached=3600):
        cache = zeep.cache.SqliteCache(timeout=cached) if cached else None
        # todo: Custom transport to enable binary encoding
        transport = zeep.transports.Transport(cache=cache)
        self.client = zeep.Client(
            wsdl='https://addons.forgesvc.net/AddOnService.svc?singleWsdl',
            port_name='WsHttpAddOnServiceEndpoint',
            service_name='AddOnService',
            plugins=[LoginClient(username, password)],
            transport=transport
        )
        # noinspection PyProtectedMember
        self.service = {
            k: OperationWrapper(k, self.client)
            for k in self.client.service._binding._operations
        }
        if self.__doc__ is None:
            self.__doc__ = ''
        self.__doc__ += 'List of available service functions: \n      ' + \
                        '\n      '.join(map(str, self.service.values()))

    @classmethod
    def from_file(cls, file='account.json'):
        with open(file, 'r') as f:
            account = json.load(f)
            return cls(account['Username'], account['Password'])

    def __str__(self) -> str:
        return str(self.__doc__)

    def __repr__(self) -> str:
        return '<{}>'.format(self.__class__.__name__)
