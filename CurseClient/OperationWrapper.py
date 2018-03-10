import collections

import zeep
import zeep.wsdl
import zeep.wsdl.bindings
import json

from .helpers import encode_json


class OperationWrapper:
    """
    Wrapper around zeep's OperationProxy to make arguments accept ArrayOf parameters
    Outputs normalized dict
    """
    # noinspection PyProtectedMember
    def __init__(self, name: str, client: zeep.Client, redis):
        self.name = name
        self.client = client
        self.redis = redis
        self.redis_pefix = 'zeep-operationcache-{}-'.format(name)
        self.proxy: zeep.client.OperationProxy = client.service[name]
        self.operation: zeep.wsdl.bindings.soap.SoapOperation = client.service._binding._operations[name]
        self.parameters = self.operation.input.body.type.elements
        self.output = self.operation.output.body.type.elements[0][1].type

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
            typed[k] = assign(k, v)

        return typed

    @classmethod
    def serialize_object(cls, obj):
        if isinstance(obj, list):
            return [cls.serialize_object(sub) for sub in obj]

        if isinstance(obj, (dict, zeep.xsd.AnyObject)):
            raise ValueError('Illegal Type')
            # todo: handle
            pass

        if isinstance(obj, (dict, zeep.xsd.CompoundValue)):
            # noinspection PyProtectedMember
            if obj._xsd_type.name.startswith('ArrayOf'):
                if len(dir(obj)) == 1:
                    return cls.serialize_object(obj[dir(obj)[0]])
            return {k: cls.serialize_object(obj[k]) for k in obj}

        return obj

    def __call__(self, *args, **kwargs):
        input_args = self.parse_args(self.parameters, *args, **kwargs)
        if self.redis:
            key = self.redis_pefix + json.dumps(input_args, separators=(',', ':'), default=encode_json)
            output = self.redis.get(key)
            if output is not None:
                # noinspection PyBroadException
                try:
                    return json.loads(output)
                except BaseException:  # This is just in case the value got corrupted somehow
                    self.redis.expire(key, 0)
                    pass

        output = self.serialize_object(self.proxy(**input_args))
        output = None if isinstance(output, dict) and all(x is None for x in output.values()) else output
        if output and self.redis:
            # noinspection PyUnboundLocalVariable
            self.redis.set(key, json.dumps(output, separators=(',', ':'), default=encode_json), ex=60*60)
        return output

    def __str__(self) -> str:
        return str(self.__doc__)

    def __repr__(self) -> str:
        return '<{} {}>'.format(self.__class__.__name__, self.__doc__)
