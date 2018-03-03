import zeep
import zeep.cache
import zeep.transports
import zeep.wsdl
import zeep.wsdl.bindings
import zeep.helpers
import zeep.xsd
import json
import datetime
import collections

from .Login import LoginClient


def encode_json(obj):
    """
    Use as `default` parameter when calling `json.dump(s)` to encode datetimes and zeep complex types
    :param obj:
    :return:
    """
    if obj is None:
        return
    if isinstance(obj, datetime.datetime):
        return obj.replace(microsecond=0).isoformat()
    # Next case is almost zeep.helpers.serialize_object(obj), but it handles 'ArrayOf' types better
    if isinstance(obj, zeep.xsd.valueobjects.CompoundValue):
        # noinspection PyProtectedMember
        if obj._xsd_type.name.startswith('ArrayOf') and len(dir(obj)) == 1:
            return obj[dir(obj)[0]]
        return {key: obj[key] for key in obj}
    return dir(obj)


def document_type(t):
    pass


class OperationWrapper:
    """
    Wrapper around zeep's OperationProxy to make arguments accept ArrayOf parameters
    Outputs normalized dict
    """
    # noinspection PyProtectedMember
    def __init__(self, name: str, client: zeep.Client):
        self.name = name
        self.client = client
        self.proxy: zeep.client.OperationProxy = client.service[name]
        self.operation: zeep.wsdl.bindings.soap.SoapOperation = client.service._binding._operations[name]
        self.parameters = self.operation.input.body.type.elements

        self.__doc__ = "{}({}) -> {}".format(self.name,
                                             document_type(self.operation.input.body.type),
                                             document_type(self.operation.input.body.type))

    @classmethod
    def parse_args(cls, parameters, *args, **kwargs):
        """
        Recursively resolves parameter arrays

        :param parameters: list of (name, element)
        :param args: provided args
        :param kwargs:  provided kwargs
        :return: dict of name: value, with value's recursively resolved
        """
        parameters = collections.OrderedDict(parameters)
        parameters_names = list(parameters.keys())

        if len(args) > len(parameters):
            raise TypeError("Too many args given")
        if len(kwargs.keys() - parameters.keys()) != 0:
            raise TypeError("Unexpected kwargs: {}".format(', '.join(kwargs.keys() - parameters.keys())))

        def assign(key, val):
            if isinstance(parameters[key].type, zeep.xsd.ComplexType):
                if isinstance(val, dict):
                    return cls.parse_args(parameters[key].type.elements, **val)
                elif isinstance(val, list) or isinstance(val, tuple):
                    return cls.parse_args(parameters[key].type.elements, *val)
                else:
                    raise TypeError("Subtype complex, must be provided as list/tuple or dict for key {}".format(key))
            else:
                return parameters[key](val)

        typed = {}

        for i in range(len(args)):
            if parameters_names[i] in typed:
                raise TypeError("Duplicate arg: {}".format(parameters_names[i]))
            typed[parameters_names[i]] = assign(parameters_names[i], args[i])

        for k, v in kwargs.items():
            if k in typed:
                raise TypeError("Duplicate kwarg: {}".format(k))
            typed[v] = assign(k, v)

        return typed

    @classmethod
    def serialize_object(cls, obj):
        if isinstance(obj, list):
            return [cls.serialize_object(sub) for sub in obj]

        if isinstance(obj, (dict, zeep.xsd.valueobjects.CompoundValue)):
            # noinspection PyProtectedMember
            if obj._xsd_type.name.startswith('ArrayOf') and len(dir(obj)) == 1:
                return obj[dir(obj)[0]]
            return {k: cls.serialize_object(obj[k]) for k in obj}

        return obj

    def __call__(self, *args, **kwargs):
        reply = self.proxy(**self.parse_args(self.parameters, *args, **kwargs))
        print(reply)
        return self.serialize_object(reply)


class CurseClient:
    def __init__(self, username, password, cached=True):
        cache = zeep.cache.SqliteCache() if cached else None
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

    @classmethod
    def from_file(cls, file='account.json'):
        with open(file, 'r') as f:
            account = json.load(f)
            return cls(account['Username'], account['Password'])

    def list_functions(self):
        return filter(lambda x: not x.startswith('_'), dir(self.client.service))

    def debug(self):
        print('Debug CurseClient')
        print('  List of services:', *self.list_functions(), sep='\n   - ')
