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
    def __init__(self, login_client, redis_store=None):
    # def __init__(self, username, password, redis_store=None):
        cache = RedisCache(redis_store) if redis_store else None
        # todo: Custom transport to enable binary encoding
        transport = zeep.transports.Transport(cache=cache)
        self.login_client = login_client
        #self.client = zeep.Client(
        #    wsdl='https://addons.forgesvc.net/AddOnService.svc?singleWsdl',
        #    port_name='WsHttpAddOnServiceEndpoint',
        #    service_name='AddOnService',
        #    plugins=[self.login_client],
        #    transport=transport,
        #    strict=False,
        #)
        # self.operations = list(self.client.service._binding._operations.keys())
        # service_type = collections.namedtuple('Service', self.operations)
        # self.service = service_type(**{k: OperationWrapper(k, self.client, redis_store) for k in self.operations})
        self.service = []
        self.operations = []
        if self.__doc__ is None:
            self.__doc__ = ''
        self.__doc__ += 'List of available service functions: \n      ' + \
                        '\n      '.join(self.operations)

    @classmethod
    def from_file(cls, file='account.json'):
        with open(file, 'r') as f:
            account = json.load(f)
            return cls(account['Username'], account['Password'])

    def __str__(self) -> str:
        return str(self.__doc__)

    def __repr__(self) -> str:
        return '<{}>'.format(self.__class__.__name__)


class RedisCache(zeep.cache.Base):
    def __init__(self, redis_store, prefix='zeep-transportcache-', expire_time=60*60*24):
        self.expire_time = expire_time
        self.prefix = prefix
        self.redis = redis_store

    def add(self, url, content):
        self.redis.set(self.prefix + url, content, ex=self.expire_time)
        return content

    def get(self, url):
        return self.redis.get(self.prefix + url)
