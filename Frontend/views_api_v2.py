import collections

import zeep.xsd.types

from . import app
from . import curse
from .helpers import to_json_response

WHITELIST = [
    'GetAddOn',
    'GetRepositoryMatchFromSlug',
    # 'GetChangeLog',
    'v2GetChangeLog',
    # 'GetAddOnDescription',
    'v2GetAddOnDescription',
    'GetAddOnFile',
    # 'GetAddOns',
    'v2GetAddOns',
    # 'GetFingerprintMatches',
    'v2GetFingerprintMatches',
    'GetFuzzyMatches',
    # 'GetDownloadToken',
    # 'GetSecureDownloadToken',
    # 'GetSyncProfile',
    # 'CreateSyncGroup',
    # 'JoinSyncGroup',
    # 'LeaveSyncGroup',
    # 'SaveSyncSnapshot',
    # 'SaveSyncTransactions',
    # 'GetAddOnDump',
    # # 'ResetAllAddonCache',
    # # 'ResetSingleAddonCache',
    'HealthCheck',
    'ServiceHealthCheck',
    'CacheHealthCheck',
    'GetAllFilesForAddOn',
    'GetAddOnFiles',
    # # 'LogDump',
    # 'ListFeeds',
    # 'ResetFeeds'
]

Documentation = collections.namedtuple('Documentation', ['url', 'method', 'inp', 'outp'])
DOCS = collections.OrderedDict()
_TYPES = {
    str: 'string',
    int: 'int',
    float: 'float',
}


class ComplexTypeException(Exception):
    pass


def resolve_types(t: zeep.xsd.Any):
    if isinstance(t, zeep.xsd.AnySimpleType):
        return t.name
    elif isinstance(t, zeep.xsd.ComplexType):
        if t.name.startswith('ArrayOf') and len(t.elements) == 1:
            return [resolve_types(t.elements[0][1].type)]
        return {
            k: resolve_types(v.type) for k, v in t.elements
        }
    else:
        return '???'


def add_views():

    def _api_call(n):
        def f(**kwargs):
            return to_json_response(getattr(curse.service, n)(**kwargs))

        return f

    for name in curse.operations:
        if name not in WHITELIST:
            continue
        try:
            service = getattr(curse.service, name)

            parameters = collections.OrderedDict()
            parameter_types = []
            for k, t in service.parameters:
                if not isinstance(t.type, zeep.xsd.AnySimpleType):
                    raise ComplexTypeException()
                # Idk if this is a good idea, now it will only accept the first type
                t = t.type.accepted_types[0]
                parameters[k] = t
                parameter_types.append('<{}:{}>'.format(_TYPES[t], k) if t in _TYPES else '<{}>'.format(k))

            output = resolve_types(service.output)

            f = _api_call(name)
            rule = '/api/v2/{}/{}'.format(name, '/'.join(parameter_types))
            endpoint = 'api_v2_{}'.format(name)
            app.add_url_rule(rule=rule, endpoint=endpoint, view_func=f)

            DOCS[name] = Documentation(url=rule, method='GET', inp=parameters, outp=output)

        except ComplexTypeException:
            # todo
            print('Skipped', name)
            pass
