
from . import exceptions
from . import types_comparator


class Checker:
    __slots__ = ()

    def check(self, stored, checked):
        if stored.name != checked.name:
            raise ValueError(f'variable names of "{stored}" and "{checked}" MUST be equal')

        return False


class SkipVariables(Checker):
    __slots__ = ('_names',)

    def __init__(self, names):
        self._names = names

    def check(self, stored, checked):
        if super().check(stored, checked):
            return True

        if stored.name in self._names:
            return True

        return False


class StrongTypeEquality(Checker):
    __slots__ = ()

    def check(self, stored, checked):
        if super().check(stored, checked):
            return True

        if stored.assigment_type == checked.assigment_type:
            return True

        return False


class AnnotationEquality(Checker):
    __slots__ = ()

    def check(self, stored, checked):
        if super().check(stored, checked):
            return True

        if stored.annotation_type is None and checked.annotation_type is None:
            return False

        if not types_comparator.compare(stored.assigment_type,
                                        checked.annotation_type):
            raise exceptions.TypeMistmatch(stored, checked)

        return True
