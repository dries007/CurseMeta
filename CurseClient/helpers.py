import datetime
import zeep


def encode_json(obj):
    """
    Use as `default` parameter when calling `json.dump(s)` to encode datetime and zeep complex types
    Handles ArrayOf* specially
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


def document_type(t: zeep.xsd.Type):
    """
    Turn type into string representation
    Handles ArrayOf* specially
    :param t:
    :return:
    """
    if isinstance(t, zeep.xsd.ComplexType):
        if t.name.startswith('ArrayOf') and len(t.elements) == 1:
            return '[%s]' % document_type(t.elements[0][1].type)
        parts = []
        for k, v in t.elements:
            parts.append('%s: %s' % (k, document_type(v.type)))
        return '%s{%s}' % (t.name, ', '.join(parts))
    return t.name
