
import pytest

from coulson import tracers
from coulson import mergers
from coulson import namespaces
from coulson import exceptions

from .examples import simple


def tracer():
    spaces = [namespaces.Namespace('tests.examples',
                                   mergers=[mergers.SkipVariables(['self']),
                                            mergers.TypeDependency()])]
    return tracers.Tracer(spaces)


def test_assigned_type_mismatch():
    with tracer().trace():
        with pytest.raises(exceptions.TypeMistmatch) as error:
            simple.assigned_type_mismatch()

    assert error.value.name == 'x'
    assert error.value.stored_type == int
    assert error.value.new_type == str
    assert error.value.file.endswith('simple.py')
    assert isinstance(error.value.line, int)


def test_annotation_type_mismatch():
    with tracer().trace():
        with pytest.raises(exceptions.TypeAnnotationMismatch) as error:
            simple.annotation_type_mismatch()

    assert error.value.name == 'x'
    assert error.value.type == str
    assert error.value.annotation == int
    assert error.value.file.endswith('simple.py')
    assert isinstance(error.value.line, int)


def test_assigned_type_mismatch_between_calls():
    with tracer().trace():
        simple.assigned_type_mismatch_between_calls(True)

        with pytest.raises(exceptions.TypeMistmatch) as error:
            simple.assigned_type_mismatch_between_calls(False)

    assert error.value.name == 'x'
    assert error.value.stored_type == int
    assert error.value.new_type == str
    assert error.value.file.endswith('simple.py')
    assert isinstance(error.value.line, int)
