
import pretty_errors

from . import example
from . import tracers


ALLOWED_NAMESPACES = ['coulson']

tracer = tracers.Tracer()

tracer.initialize(ALLOWED_NAMESPACES)

with tracer.trace():
    z = example.test_function('13')

print(z)

# print(typing.get_type_hints(x, include_extras=False))
