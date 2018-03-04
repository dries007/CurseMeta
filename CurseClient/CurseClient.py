import zeep
import zeep.cache
import json
import collections

from .Login import LoginClient
from .OperationWrapper import OperationWrapper


class CurseClient:
    """
    Curse SOAP API client
    """

    # noinspection PyProtectedMember
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
        self.operations = list(self.client.service._binding._operations.keys())
        service_type = collections.namedtuple('Service', self.operations)
        self.service = service_type(**{k: OperationWrapper(k, self.client) for k in self.operations})
        if self.__doc__ is None:
            self.__doc__ = ''
        self.__doc__ += 'List of available service functions: \n      ' + \
                        '\n      '.join(self.operations)

    @classmethod
    def from_file(cls, file='account.json', cached=3600):
        with open(file, 'r') as f:
            account = json.load(f)
            return cls(account['Username'], account['Password'], cached=cached)

    def __str__(self) -> str:
        return str(self.__doc__)

    def __repr__(self) -> str:
        return '<{}>'.format(self.__class__.__name__)
