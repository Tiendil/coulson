import sys
import contextlib

from . import types_comparators
from . import exceptions
from . import inspectors
from . import namespaces


def construct_variable(name, expected_type, is_annotation, filename, line):
    return namespaces.Variable(name=name,
                               expected_type=expected_type,
                               is_annotation=is_annotation,
                               file=filename,
                               line=line)


def analyze_variable(frame, function, namespace, name, value):

    annotation_type = None

    # TODO: make find_annotations functionality configurable
    for annotation in inspectors.find_annotations(frame, function, name):

        if annotation_type is None:
            annotation_type = annotation
            continue

        # TODO: check if annotations is related to each other
        #       or remove check at all, since annotations produced by programmers and they know what doing
        if annotation_type is not annotation:
            raise AnnotationsMistmatch(name, annotation_type, annotation)

    value_type = type(value)

    new_type = value_type

    is_annotation = False

    if annotation_type is not None:
        if types_comparators.is_subtype_or_equal(new_type, annotation_type):
            new_type = annotation_type
            is_annotation = True
        else:
            raise exceptions.TypeAnnotationMismatch(name,
                                                    value_type,
                                                    annotation_type,
                                                    frame.f_code.co_filename,
                                                    frame.f_lineno)

    stored_variable = namespace.get(name)

    if stored_variable is None:
        namespace.register(construct_variable(name,
                                              new_type,
                                              is_annotation,
                                              frame.f_code.co_filename,
                                              frame.f_lineno))
        return

    for merger in namespace.mergers:
        if merger.merge(stored_variable, new_type, is_annotation):
            return

    raise exceptions.TypeMistmatch(name,
                                   stored_variable.expected_type,
                                   stored_variable.is_annotation,
                                   new_type,
                                   is_annotation,
                                   frame.f_code.co_filename,
                                   frame.f_lineno)


class Tracer:
    __slots__ = ('_namespaces', 'is_tracing', '_mergers', '_namespaces_cache')

    def __init__(self, namespaces):
        self._namespaces = namespaces
        self.is_tracing = False
        self._namespaces_cache = {}

    def start_tracing(self):
        sys.settrace(self.trace_callback)
        self.is_tracing = True

    def stop_tracing(self):
        sys.settrace(None)
        self.is_tracing = False

    @contextlib.contextmanager
    def trace(self):
        try:
            self.start_tracing()

            yield

        finally:
            self.stop_tracing()

    def trace_callback(self, frame, event, arg):

        filename = frame.f_code.co_filename

        if filename not in self._namespaces_cache:
            for namespace in self._namespaces:
                if namespace.filter.check_frame(filename):
                    self._namespaces_cache[filename] = namespace
                    break
            else:
                self._namespaces_cache[filename] = None

        found_namespace = self._namespaces_cache[filename]

        if found_namespace is None:
            return

        function = inspectors.determine_function(frame)

        if function is None:
            return

        # function_namespace = logic.function_namespace(function)

        for name in inspectors.frame_variables(frame):
            initialized, value = inspectors.frame_variable_value(frame, name)

            if not initialized:
                continue

            analyze_variable(frame, function, found_namespace, name, value)

        # faster
        frame.f_trace_lines = True
        frame.f_trace_opcodes = False

        # accuracy
        # frame.f_trace_lines = False
        # frame.f_trace_opcodes = True

        # setup trace function in frame, to not write it from every return statement
        frame.f_trace = self.trace_callback

        return
