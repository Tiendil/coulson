
import dataclasses


@dataclasses.dataclass
class Variable:
    __slots__ = ('name', 'expected_type', 'file', 'line')

    name: str
    expected_type: type
    file: str
    line: int


class Namespace:
    __slots__ = ('_variables', 'id', 'mergers')

    def __init__(self, id, mergers):
        self.id = id
        self.mergers = mergers
        self._variables = {}

    def get(self, name, default=None):
        return self._variables.get(name, default)

    def register(self, variable):
        if variable.name in self._variables:
            raise ValueError(f'Variable {variable.name} has registered already.')

        self._variables[variable.name] = variable

    def can_capture(self, namespace_id):
        return namespace_id.startswith(self.id)

    def __in__(self, name):
        return name in self._variables
