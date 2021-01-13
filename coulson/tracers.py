import sys
import inspect
import warnings
import contextlib

from . import types_comparators
from . import exceptions
from . import inspectors
from . import namespaces
from . import logic


def construct_variable(frame_info, name, expected_type):
    return namespaces.Variable(name=name,
                               expected_type=expected_type,
                               file=frame_info.filename,
                               line=frame_info.lineno)


def analyze_variable(frame, function, namespace, name):

    initialized, value = inspectors.frame_variable_value(frame, name)

    if not initialized:
        return

    frame_info = inspect.getframeinfo(frame)

    annotation_type = None

    # TODO: make find_annotations functionality configurable
    for annotation in inspectors.find_annotations(frame, function, name):

        if annotation_type is None:
            annotation_type = annotation
            continue

        # TODO: check if annotations is related to each other
        #       or remove check at all, since annotations produced by programmer and they know what doing
        if annotation_type is not annotation:
            raise AnnotationsMistmatch(name, annotation_type, annotation)

    value_type = type(value)

    new_type = value_type

    print(f'{new_type=} {annotation_type=}')

    if annotation_type is not None:
        if types_comparators.is_subtype_or_equal(new_type, annotation_type):
            new_type = annotation_type
        else:
            raise exceptions.TypeAnnotationMismatch(name,
                                                    value_type,
                                                    annotation_type,
                                                    frame_info.filename,
                                                    frame_info.lineno)

    stored_variable = namespace.get(name)

    if stored_variable is None:
        namespace.register(construct_variable(frame_info, name, new_type))
        return

    for merger in namespace.mergers:
        if merger.merge(stored_variable, new_type):
            return

    raise exceptions.TypeMistmatch(name,
                                   stored_variable.expected_type,
                                   new_type,
                                   frame_info.filename,
                                   frame_info.lineno)


class Tracer:
    __slots__ = ('_namespaces', 'initialized', '_mergers')

    def __init__(self, namespaces):
        self._namespaces = namespaces

    def start_tracing(self):
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

        for namespace in self._namespaces:
            if not namespace.can_capture(function_namespace):
                continue

            for name in inspectors.frame_variables(frame):
                analyze_variable(frame, function, namespace, name)

            break

        return
