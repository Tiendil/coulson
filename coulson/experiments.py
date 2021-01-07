# TODO: there can be some problems in working with closures

import sys
import weakref
import inspect
import warnings

import pretty_errors

from . import namespaces
from . import inspectors
from . import example
from . import logic


FUNCTIONS_CACHE = weakref.WeakValueDictionary()

ALLOWED_NAMESPACES = ['coulson']

NAMESPACES = namespaces.Container(ALLOWED_NAMESPACES)


def determine_function(frame):
    function = FUNCTIONS_CACHE.get(frame.f_code)

    if function is not None:
        return function

    return inspectors.search_function(frame)


def construct_variable(frame, name, value):
    frame_info = inspect.getframeinfo(frame)

    # TODO: fill and check annotations
    return namespaces.Variable(name=name,
                               annotation_type=None,
                               assigment_type=type(value),
                               file=frame_info.filename,
                               line=frame_info.lineno)


class TypeMistmatch(Exception):

    def __init__(self, stored_variable, current_variable):
        message = ('Type mismatch\n'
                   f'stored variable: {stored_variable}\n',
                   f'current variable: {current_variable}')

        super().__init__(message)


def analyze_variable(frame, namespace, name):

    initialized, value = inspectors.frame_variable_value(frame, name)

    print(name, initialized, value)

    if not initialized:
        return

    stored_varible = namespace.get(name)

    if stored_varible is None:
        namespace.register(construct_variable(frame, name, value))
        return

    # TODO: rewrite to complex check
    if stored_varible.assigment_type != type(value):
        raise TypeMistmatch(stored_varible, construct_variable(frame, name, value))


def trace(frame, event, arg):

    frame.f_trace_lines = False
    frame.f_trace_opcodes = True

    # setup trace function in frame, to not write it from every return statement
    frame.f_trace = trace

    function = determine_function(frame)

    if function is None:
        warnings.warn(f'can not found function for frame {frame}')
        return

    function_namespace = logic.function_namespace(function)

    namespace = NAMESPACES.find(function_namespace)

    if namespace is None:
        return

    print('NAMESPACE:', namespace.id)

    print('-----------')
    print(inspect.getframeinfo(frame))
    print('co_cellvars', frame.f_code.co_cellvars)
    print('co_freevars', frame.f_code.co_freevars)
    print('co_names', frame.f_code.co_names)
    print('co_varnames', frame.f_code.co_varnames)
    print('co_varnames', frame.f_code.co_varnames)

    for name in inspectors.frame_variables(frame):
        analyze_variable(frame, namespace, name)

    return


sys.settrace(trace)


z = example.test_function('13')

print(z)

# print(typing.get_type_hints(x, include_extras=False))
