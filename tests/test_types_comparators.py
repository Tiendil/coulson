
import typing

from hypothesis import given
from hypothesis import strategies as h_st

from coulson import types_comparators

from . import types_for_tests


class TestIsSubtypeOrEqual:

    @given(h_st.sampled_from(types_for_tests.COMMON_TYPES))
    def test_optional_common_types(self, common_type):
        assert types_comparators.is_subtype_or_equal(typing.Optional[common_type], common_type)
