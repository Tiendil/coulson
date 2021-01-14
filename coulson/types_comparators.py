
import typing
import functools


def get_origin(type):
    return getattr(type, '__origin__', None)


def is_union(type):
    return get_origin(type) is typing.Union


def is_any(type):
    return type is typing.Any


def has_parameters(type):
    return bool(getattr(type, '__parameters__'))


@functools.cache
def is_subtype_or_equal(type, description):

    if is_any(type) or is_any(description):
        return True

    # print('is_subtype_or_equal…')
    # print(f'{type=} {description=}')

    origin = get_origin(description)

    # print(f'{origin=}')

    if origin is None:
        return compare_hierarchy(type, description)

    if is_union(description):
        return is_subset_of_union(type, description)

    return compare_hierarchy(type, origin)


@functools.cache
def compare_hierarchy(type, description):
    origin = get_origin(type)

    if origin is None:
        # print(f'compare_hierarchy {type=}, {description=}, {type is description or isinstance(type, description)}')
        return type is description or isinstance(type, description)

    if is_union(type):
        return all(is_subtype_or_equal(type_arg, description)
                   for type_arg in type.__args__)

    return compare_hierarchy(origin, description)


@functools.cache
def is_subset_of_union(type, description):
    if not is_union(type):
        return any(is_subtype_or_equal(type, union_type)
                   for union_type in description.__args__)

    for type_arg in type.__args__:
        if not any(is_subtype_or_equal(type_arg, union_type)
                   for union_type in description.__args__):
            return False

    return True
