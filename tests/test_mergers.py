
import random

import pytest

from hypothesis import given, assume
from hypothesis import strategies as h_st

from coulson import mergers
from coulson import types_comparators

from . import strategies as c_st


class TestSkipVariables:

    def merge(self, names, variable, new_type):
        merger = mergers.SkipVariables(names=names)
        return merger.merge(variable, new_type)

    @given(c_st.variables(), c_st.types, h_st.lists(c_st.variable_names, min_size=1))
    def test_success(self, variable, new_type, merger_names):

        variable.name = random.choice(merger_names)

        assert self.merge(merger_names, variable, new_type)

    @given(c_st.variables(), c_st.types, h_st.lists(c_st.variable_names))
    def test_continue(self, variable, new_type, merger_names):
        assume(variable.name not in merger_names)

        assert not self.merge(merger_names, variable, new_type)


class TestTypeDependency:

    def merge(self, variable, new_type):
        merger = mergers.TypeDependency()
        return merger.merge(variable, new_type)

    @given(c_st.variables())
    def test_types_is_equal(self, variable):
        assert self.merge(variable, variable.expected_type)

    @given(c_st.variables(), c_st.types_with_annotations())
    def test_new_type_is_subtype(self, variable, type_with_annotation):

        # expected_type must be parent of new_type
        new_type, variable.expected_type = type_with_annotation
        assert self.merge(variable, new_type)

    @given(c_st.variables(), c_st.types)
    def test_types_not_equals(self, variable, new_type):
        assume(not types_comparators.is_subtype_or_equal(new_type, variable.expected_type))
        assert not self.merge(variable, new_type)
