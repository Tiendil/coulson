
import typing


def get_origin(type):
    return getattr(type, '__origin__', None)


def is_union(type):
    return get_origin(type) is typing.Union


def has_parameters(type):
    return bool(getattr(type, '__parameters__'))


def compare(type, description):

    origin = get_origin(description)

    if origin is None:
        return compare_hierarchy(type, description)

    if is_union(type):
        return any(compare(type, arg)
                   for arg in description.__args__)

    return compare_hierarchy(type, origin)


def compare_hierarchy(type, description):
    return type is description or isinstance(type, description)
