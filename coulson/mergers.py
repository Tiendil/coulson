
from . import types_comparators


class Merger:
    __slots__ = ()

    def merge(self, variable, new_type):
        raise NotImplementedError('Method must be redefined in child class')


class SkipVariables(Merger):
    __slots__ = ('_names',)

    def __init__(self, names):
        self._names = names

    def merge(self, variable, new_type):
        return variable.name in self._names


class TypeDependency(Merger):
    __slots__ = ()

    def merge(self, variable, new_type):
        return types_comparators.is_subtype_or_equal(new_type, variable.expected_type)


class HasNotBaseCommonType(Merger):
    __slots__ = ('_base_types')

    def __init__(self, base_types=(object, type, Exception)):
        self._base_types = base_types

    def merge(self, variable, new_type):
        # TODO: check if class/annotation trees has common members
        raise NotImplementedError('TODO: implement')
