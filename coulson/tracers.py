import sys
import inspect
import warnings
import contextlib

from . import inspectors
from . import namespaces
from . import logic


class TypeMistmatch(Exception):

    def __init__(self, stored_variable, current_variable):
        message = ('Type mismatch\n'
                   f'stored variable: {stored_variable}\n',
                   f'current variable: {current_variable}')

        super().__init__(message)


def construct_variable(frame, name, value):
    frame_info = inspect.getframeinfo(frame)

    # TODO: fill and check annotations
    return namespaces.Variable(name=name,
                               annotation_type=None,
                               assigment_type=type(value),
                               file=frame_info.filename,
                               line=frame_info.lineno)


def analyze_variable(frame, namespace, name):

    initialized, value = inspectors.frame_variable_value(frame, name)

    if not initialized:
        return

    stored_varible = namespace.get(name)

    if stored_varible is None:
        namespace.register(construct_variable(frame, name, value))
        return

    # TODO: rewrite to complex check
    if stored_varible.assigment_type != type(value):
        raise TypeMistmatch(stored_varible, construct_variable(frame, name, value))


class Tracer:
    __slots__ = ('_namespaces', 'initialized')

    def __init__(self):
        self.initialized = False
        self._namespaces = None

    def initialize(self, allowed_namespaces):
        self._namespaces = namespaces.Container(allowed_namespaces)
        self.initialized = True

    def start_tracing(self):
        if not self.initialized:
            raise Exception('Tracer is not initialized')

        sys.settrace(self.trace_callback)

    def stop_tracing(self):
        sys.settrace(None)

    @contextlib.contextmanager
    def trace(self):
        try:
            self.start_tracing()

            yield

        finally:
            self.stop_tracing()

    def trace_callback(self, frame, event, arg):

        frame.f_trace_lines = False
        frame.f_trace_opcodes = True

        # setup trace function in frame, to not write it from every return statement
        frame.f_trace = self.trace_callback

        function = inspectors.determine_function(frame)

        if function is None:
            warnings.warn(f'can not found function for frame {frame}')
            return

        function_namespace = logic.function_namespace(function)

        namespace = self._namespaces.find(function_namespace)

        if namespace is None:
            return

        # print('-----------')
        # print('NAMESPACE:', namespace.id)
        # print(inspect.getframeinfo(frame))
        # print('co_cellvars', frame.f_code.co_cellvars)
        # print('co_freevars', frame.f_code.co_freevars)
        # print('co_names', frame.f_code.co_names)
        # print('co_varnames', frame.f_code.co_varnames)
        # print('co_varnames', frame.f_code.co_varnames)

        for name in inspectors.frame_variables(frame):
            analyze_variable(frame, namespace, name)

        return
