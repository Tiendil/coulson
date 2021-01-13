
import typing


def get_origin(type):
    return getattr(type, '__origin__', None)


def is_union(type):
    return get_origin(type) is typing.Union


def has_parameters(type):
    return bool(getattr(type, '__parameters__'))


def is_subtype_or_equal(type, description):

    # print('is_subtype_or_equal…')
    # print(f'{type=} {description=}')

    origin = get_origin(description)

    # print(f'{origin=}')

    if origin is None:
        return compare_hierarchy(type, description)

    if is_union(description):
        return is_subset_of_union(type, description)

    return compare_hierarchy(type, origin)


def compare_hierarchy(type, description):
    # print(f'compare_hierarchy {type=}, {description=}, {type is description or isinstance(type, description)}')
    return type is description or isinstance(type, description)


def is_subset_of_union(type, description):
    if not is_union(type):
        return any(is_subtype_or_equal(type, union_type)
                   for union_type in description.__args__)

    for type_arg in type.__args__:
        if not any(is_subtype_or_equal(type_arg, union_type)
                   for union_type in description.__args__):
            return False

    return True
