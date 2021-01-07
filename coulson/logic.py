

def function_namespace(function):
    return f'{function.__module__}.{function.__qualname__}'
