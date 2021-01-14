
import re
import dataclasses


@dataclasses.dataclass
class Variable:
    __slots__ = ('name', 'expected_type', 'is_annotation', 'file', 'line')

    name: str
    expected_type: type
    is_annotation: bool
    file: str
    line: int


@dataclasses.dataclass
class Filter:
    __slots__ = ()


@dataclasses.dataclass
class ModulePath(Filter):
    __slots__ = ('base_path',)

    base_path: str

    def check_frame(self, filename):
        return filename.startswith(self.base_path)


@dataclasses.dataclass
class ModulePathRE(Filter):
    __slots__ = ('expression', '_compiled_expression')

    expression: str
    _compiled_expression: re.Pattern

    def __init__(self, expression):
        self.expression = expression
        self._compiled_expression = re.compile(expression)

    def check_frame(self, filename):
        return self._compiled_expression.search(filename) is not None


@dataclasses.dataclass
class Chained(Filter):
    __slots__ = ('filters',)

    filters: list

    def check_frame(self, filename):
        return all(filter.check_frame(filename) for filter in self.filters)


class Namespace:
    __slots__ = ('_variables', 'id', 'mergers', 'filter')

    def __init__(self, id, mergers, filter):
        self.id = id
        self.mergers = mergers
        self._variables = {}
        self.filter = filter

    def get(self, name, default=None):
        return self._variables.get(name, default)

    def register(self, variable):
        if variable.name in self._variables:
            raise ValueError(f'Variable {variable.name} has registered already.')

        self._variables[variable.name] = variable

    # def can_capture(self, namespace_id):
    #     return namespace_id.startswith(self.id)

    def __in__(self, name):
        return name in self._variables
