
import gc
import sys
import typing
import weakref
import inspect
import warnings


def search_function_in_locals(frame, code):
    for value in frame.f_locals.values():

        # if not hasattr(value, '__code__'):
        #     continue

        if not inspect.isfunction(value):
            continue

        if value.__code__ is code:
            yield value


def search_function_in_globals(frame, code):
    for name, value in frame.f_globals.items():

        if not inspect.isfunction(value):
            continue

        # if not hasattr(value, '__code__'):
        #     continue

        if name in frame.f_locals:
            continue

        if value.__code__ is code:
            yield value


def search_function_in_gc(code):
    # there are can be more then one function with same code
    # in that case, return None
    # TODO: determine that cases and do something with them

    function = None

    for candidate in gc.get_referrers(code):
        if not inspect.isfunction(candidate):
            continue

        # if (not inspect.isfunction(candidate) and
        #     not inspect.ismethod(candidate)):
        #     continue

        if function is not None:
            return None

        function = candidate

    return function


def search_module(code):
    for module in sys.modules.values():
        if getattr(module, '__file__', None) == code.co_filename:
            return module

    return None


def search_function_in_variables(frame, code):
    candidates = []

    candidates.extend(search_function_in_locals(frame, code))
    candidates.extend(search_function_in_globals(frame, code))

    if not candidates:
        return None

    result = candidates[0]

    for candidate in candidates:
        if result is not candidate:
            return None

    return result


def is_system_code(code):
    if code.co_filename.startswith('<'):
        return True

    if code.co_filename.startswith('<'):
        return True

    return False


def search_function(frame):
    # TODO: rewrite to cache, remove caching from search_function_in_gc
    function = None

    if is_system_code(frame.f_code):
        return True, None

    if frame.f_back:
        function = search_function_in_variables(frame.f_back, frame.f_code)

    if function is not None:
        return True, function

    function = search_function_in_gc(frame.f_code)

    if function is not None:
        return True, function

    function = search_module(frame.f_code)

    if function is not None:
        return True, function

    return False, None


def frame_variable_value(frame, name):
    if name in frame.f_locals:
        return True, frame.f_locals[name]

    if name in frame.f_globals:
        return True, frame.f_globals[name]

    if name in frame.f_builtins:
        return True, frame.f_builtins[name]

    # variable not defined
    # TODO: check that logic
    return False, None


def frame_variables(frame):
    # TODO: check if all variables received
    # TODO: check if descriptions is correct

    # variables, to be locked in closures
    for name in frame.f_code.co_cellvars:
        yield name

    # variables, locked in closures
    for name in frame.f_code.co_freevars:
        yield name

    # ????
    for name in frame.f_code.co_names:
        yield name

    # ????
    for name in frame.f_code.co_varnames:
        yield name


def determine_function(frame,
                       found_functions=weakref.WeakValueDictionary(),
                       not_found_functions=weakref.WeakKeyDictionary()):

    if frame.f_code in not_found_functions:
        return None

    function = found_functions.get(frame.f_code)

    if function is not None:
        return function

    found, function = search_function(frame)

    if not found:
        # if frame.f_code.co_filename == '/home/the_tale/current/venv/lib/python3.9/site-packages/smart_imports/rules.py':
        #     print('----------------')
        #     print(f'{frame=}')
        #     print(f'{frame.f_back=}')
        #     print(f'{frame.f_code.co_filename=}')
        #     print(f'{frame.f_code.co_flags=}')
        #     print(f'{frame.f_code.co_name=}')

        #     print(f'{list(frame_variables(frame))=}')
        #     print(f'{is_system_code(frame.f_code)=}')
        #     print(f'{search_function_in_variables(frame.f_back, frame.f_code)=}')
        #     print(f'{search_function_in_gc(frame.f_code)=}')

        warnings.warn(f'can not found function for frame {frame}')

    if function is None:
        not_found_functions[frame.f_code] = True
        return None

    if hasattr(function, '__self__'):
        # if we found bound method, get its function
        # TODO: Probably, we should not found such method?
        #       Way of founding them must be investigated, it can be a bug
        function = function.__func__

    found_functions[frame.f_code] = function

    return function


# TODO: optimize (add cache or smth equal)
# TODO: check class annotations for methods
# TODO: collect annotations recusevly from current function up to module through all namespaces
# TODO: it simce that best way to receive ALL annotations is one of:
# - parse module source at get them from AST
# - inspect module recusivly after it had imported completly
def _find_annotations(frame, function, name):
    annotation = typing.get_type_hints(function,
                                       globalns=frame.f_globals,
                                       localns=frame.f_locals).get(name)

    if annotation is not None:
        yield annotation

    # try to get annotations from class attributes
    # not best implementation
    for value in frame.f_globals.values():

        try:
            if not inspect.isclass(value):
                continue
        except Exception:
            # check can be failed by some magic objects, like Django Settings
            continue

        try:
            annotation = typing.get_type_hints(value,
                                               globalns=frame.f_globals).get(name)
        except Exception:
            # typing module raise exceptions on some values
            # TODO: refactor full fucntion
            continue

        if annotation is not None:
            yield annotation

    if not hasattr(function, '__module__'):
        # print(f'skip module of {function=}')
        # do not search annotations in functions module if that module is not imported yet
        # TODO: we should defer search to future time?
        return

    module = sys.modules[function.__module__]

    annotation = typing.get_type_hints(module,
                                       globalns=frame.f_globals,
                                       localns=frame.f_locals).get(name)

    if annotation is not None:
        yield annotation


# TODO: refactor to weakref cache
def find_annotations(frame, function, name, cache={}):  # pylint: disable=W0102

    key = (function, name)

    if key in cache:
        return cache[key]

    annotations = list(_find_annotations(frame, function, name))

    cache[key] = annotations

    return annotations
