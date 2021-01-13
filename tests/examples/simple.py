

def assigned_type_mismatch():
    x = 666
    x = '666'
    return x


def annotation_type_mismatch(x: int = '666'):
    return x


def assigned_type_mismatch_between_calls(case):
    if case:
        x = 666
    else:
        x = '666'

    return x
