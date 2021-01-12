
from . import exceptions
from . import types_comparator


class Checker:
    __slots__ = ()

    def check(self, stored, checked):
        raise NotImplementedError('Method must be redefined in child class')


class EqualNames(Checker):

    __slots__ = ()

    def check(self, stored, checked):
        if stored.name != checked.name:
            raise exceptions.TypeMistmatch(stored, checked)

        return False


class SkipVariables(Checker):
    __slots__ = ('_names',)

    def __init__(self, names):
        self._names = names

    def check(self, stored, checked):
        if stored.name in self._names:
            return True

        return False


class StrongTypeEquality(Checker):
    __slots__ = ()

    def check(self, stored, checked):
        if stored.assigment_type is None:
            return False

        if stored.assigment_type == checked.assigment_type:
            return True

        return False


class AnnotationEquality(Checker):
    __slots__ = ()

    def check(self, stored, checked):
        if stored.annotation_type is None or checked.annotation_type is None:
            return False

        if stored.annotation_type is not checked.annotation_type:
            raise exceptions.TypeMistmatch(stored, checked)

        return True
