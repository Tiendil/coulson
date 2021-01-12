
import pretty_errors

from . import example
from . import tracers
from . import checkers


ALLOWED_NAMESPACES = ['coulson']

CHECKERS = [checkers.EqualNames(),
            checkers.SkipVariables(['self']),
            checkers.AnnotationEquality(),
            checkers.StrongTypeEquality()]

tracer = tracers.Tracer()

tracer.initialize(ALLOWED_NAMESPACES, CHECKERS)

with tracer.trace():
    z = example.test_function('13')

print(z)

# print(typing.get_type_hints(x, include_extras=False))
