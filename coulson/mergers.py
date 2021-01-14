
from . import types_comparators


class Merger:
    __slots__ = ()

    def merge(self, variable, new_type, is_annotation):
        raise NotImplementedError('Method must be redefined in child class')


class SkipVariables(Merger):
    __slots__ = ('_names',)

    def __init__(self, names):
        self._names = names

    def merge(self, variable, new_type, is_annotation):
        return variable.name in self._names


class TypeDependency(Merger):
    __slots__ = ()

    def merge(self, variable, new_type, is_annotation):
        if variable.is_annotation:
            # TODO: in most cases annotations shoul be equal to each other
            #       but sometimes it is not. Like :X and :Optional[X]
            #       probably we should do smth with that
            return types_comparators.is_subtype_or_equal(new_type, variable.expected_type)

        if is_annotation:
            # annotation has priority over actual value types
            # print('------------')
            # print(f'{types_comparators.is_subtype_or_equal(variable.expected_type, new_type)=}')
            # print(f'{variable.expected_type=}, {new_type=}')
            if types_comparators.is_subtype_or_equal(variable.expected_type, new_type):
                variable.is_annotation = True
                variable.expected_type = new_type
                return True

            return False

        return types_comparators.is_subtype_or_equal(new_type, variable.expected_type)


class HasNotBaseCommonType(Merger):
    __slots__ = ('_base_types')

    def __init__(self, base_types=(object, type, Exception)):
        self._base_types = base_types

    def merge(self, variable, new_type, is_annotation):
        # TODO: check if class/annotation trees has common members
        raise NotImplementedError('TODO: implement')
