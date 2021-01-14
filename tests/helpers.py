
import copy
import contextlib


@contextlib.contextmanager
def not_changed(variable):
    orignal = copy.deepcopy(variable)

    yield

    assert variable == orignal


@contextlib.contextmanager
def changed(variable):
    orignal = copy.deepcopy(variable)

    yield

    assert variable != orignal
