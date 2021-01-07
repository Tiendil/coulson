

def create_inc(delta):
    def inc(x: int) -> int:
        return x + delta

    return inc


GLOBAL_VARIABLE = 666


def test_function(value: str, *argv, **kwargs) -> int:
    if argv:
        return -1

    if kwargs:
        return -2

    y: int = int(value)

    y = 4.5

    return create_inc(666)(y)
