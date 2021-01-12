
import decimal
import fractions
import dataclasses

# TODO: add classes from collections
# TODO: logic for generic classes


SPECIAL_TYPES = [type(None),
                 bool]


BASE_TYPES = [int,
              float,
              decimal.Decimal,
              dict,
              set,
              frozenset,
              list,
              tuple,
              type,
              object,
              fractions.Fraction,
              complex,
              Exception]


def derive_class(cls):
    class DerivedClass(cls):
        pass

    DerivedClass.__name__ = f'DerivedFrom{cls.__name__}'

    return DerivedClass


DERIVED_TYPES = [derive_class(cls) for cls in BASE_TYPES]


class ExampleA:
    pass


class ExampleB(ExampleA):
    pass


class ExampleC(ExampleA):
    pass


class ExampleD(ExampleB, ExampleC):
    pass


class ExampleE:
    pass


@dataclasses.dataclass
class ExampleDataclass:
    pass


CUSTOM_TYPES = [ExampleA,
                ExampleB,
                ExampleC,
                ExampleD,
                ExampleE,
                ExampleDataclass]


TYPES = [*SPECIAL_TYPES, *BASE_TYPES, *DERIVED_TYPES, *CUSTOM_TYPES]
