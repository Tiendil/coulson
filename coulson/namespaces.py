
import typing
import dataclasses


@dataclasses.dataclass
class Variable:
    __slots__ = ('name', 'annotation_type', 'assigment_type', 'file', 'line')

    name: str
    annotation_type: typing.Optional[type]
    assigment_type: typing.Optional[type]
    file: str
    line: int


class Namespace:
    __slots__ = ('_variables', 'id')

    def __init__(self, id):
        self.id = id
        self._variables = {}

    def get(self, name, default=None):
        return self._variables.get(name, default)

    def register(self, variable):
        if variable.name in self._variables:
            raise ValueError(f'Variable {variable.name} has registered already.')

        self._variables[variable.name] = variable

    def __in__(self, name):
        return name in self._variables


class Container:
    __slots__ = ('_namespaces', 'allowed_namespaces')

    def __init__(self, allowed_namespaces):
        self.allowed_namespaces = allowed_namespaces
        self._namespaces = {}

    def find_allowed_name(self, name):
        for id in self.allowed_namespaces:
            if name.startswith(id):
                return id

        return None

    def find(self, name):
        allowed_name = self.find_allowed_name(name)

        if allowed_name is None:
            return None

        namespace = self._namespaces.get(allowed_name)

        if namespace is not None:
            return namespace

        namespace = Namespace(allowed_name)

        self._namespaces[allowed_name] = namespace

        return namespace
