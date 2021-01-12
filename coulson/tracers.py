import sys
import inspect
import warnings
import contextlib

from . import exceptions
from . import inspectors
from . import namespaces
from . import logic


class AnnotationsMistmatch(Exception):

    def __init__(self, name, stored_annotation, new_annotation):
        message = (f'Annotation mismatch for variable "{name}"\n'
                   f'stored annotation: {stored_annotation}\n'
                   f'new annotation: {new_annotation}')

        super().__init__(message)


def construct_variable(frame, name, value):
    frame_info = inspect.getframeinfo(frame)

    # TODO: fill and check annotations
    return namespaces.Variable(name=name,
                               annotation_type=None,
                               assigment_type=type(value),
                               file=frame_info.filename,
                               line=frame_info.lineno)


def analyze_variable(frame, function, namespace, name, checkers):

    initialized, value = inspectors.frame_variable_value(frame, name)

    if not initialized:
        return

    current_variable = construct_variable(frame, name, value)

    stored_varible = namespace.get(name)

    if stored_varible is None:
        namespace.register(current_variable)
        stored_varible = current_variable

    for annotation in inspectors.find_annotations(frame, function, name):
        # TODO: here we MUST compare type to annotation
        #       to ensure, that variable is consistent

        if current_variable.annotation_type is None:
            current_variable.annotation_type = annotation
            continue

        if current_variable.annotation_type != annotation:
            raise AnnotationsMistmatch(name, current_variable.annotation_type, annotation)

    for checker in checkers:
        if checker.check(stored_varible, current_variable):
            current_variable.merge(stored_varible)
            return

    raise exceptions.TypeMistmatch(stored_varible, current_variable)


class Tracer:
    __slots__ = ('_namespaces', 'initialized', '_checkers')

    def __init__(self):
        self.initialized = False
        self._namespaces = None
        self._checkers = None

    def initialize(self, allowed_namespaces, checkers):
        self._namespaces = namespaces.Container(allowed_namespaces)
        self._checkers = checkers
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
            analyze_variable(frame, function, namespace, name, self._checkers)

        return
