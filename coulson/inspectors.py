
import gc
import weakref
import inspect


def search_function_in_locals(frame, code):
    for value in frame.f_locals.values():

        if not hasattr(value, '__code__'):
            continue

        if value.__code__ is code:
            yield value


def search_function_in_globals(frame, code):
    for name, value in frame.f_globals.items():
        if not hasattr(value, '__code__'):
            continue

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

        if function is not None:
            return None

        function = candidate

    return function


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


def search_function(frame):
    # TODO: rewrite to cache, remove caching from search_function_in_gc
    function = None

    if frame.f_back:
        function = search_function_in_variables(frame.f_back, frame.f_code)

    if function is not None:
        return function

    return search_function_in_gc(frame.f_code)


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


def determine_function(frame, cache=weakref.WeakValueDictionary()):
    function = cache.get(frame.f_code)

    if function is not None:
        return function

    return search_function(frame)
