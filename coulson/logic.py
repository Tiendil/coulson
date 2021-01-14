
import inspect


def function_namespace(function):
    if inspect.isfunction(function):
        return f'{function.__module__}.{function.__qualname__}'

    # if inspect.ismethod(function):
    #     return f'{function.__module__}.{function.__qualname__}'

    if inspect.ismodule(function):
        return function.__name__

    raise NotImplementedError(f'can not determine namespace for {function=}')
