
import random

import pytest

from hypothesis import given, assume
from hypothesis import strategies as h_st

from coulson import checkers
from coulson import exceptions
from coulson import types_comparator

from . import strategies as c_st
from . import types_for_tests


class TestEqualNames:

    def check(self, variable_1, variable_2):
        checker = checkers.EqualNames()
        return checker.check(variable_1, variable_2)

    @given(c_st.variables(), c_st.variables())
    def test_different_names(self, variable_1, variable_2):
        assume(variable_1.name != variable_2.name)

        with pytest.raises(exceptions.TypeMistmatch):
            self.check(variable_1, variable_2)

    @given(c_st.variables(), c_st.variables())
    def test_equal_names(self, variable_1, variable_2):
        variable_2.name = variable_1.name
        assert not self.check(variable_1, variable_2)


class TestSkipVariables:

    def check(self, names, variable_1, variable_2):
        checker = checkers.SkipVariables(names=names)
        return checker.check(variable_1, variable_2)

    @given(c_st.variables(), c_st.variables(), h_st.lists(c_st.variable_names, min_size=1))
    def test_success(self, variable_1, variable_2, checker_names):

        variable_1.name = random.choice(checker_names)
        variable_2.name = variable_1.name

        assert self.check(checker_names, variable_1, variable_2)

    @given(c_st.variables(), c_st.variables(), h_st.lists(c_st.variable_names))
    def test_continue(self, variable_1, variable_2, checker_names):
        assume(variable_1.name not in checker_names)

        variable_2.name = variable_1.name

        assert not self.check(checker_names, variable_1, variable_2)


class TestStrongTypeEquality:

    def check(self, variable_1, variable_2=None):
        checker = checkers.StrongTypeEquality()
        return checker.check(variable_1, variable_2)

    @given(c_st.variables(), c_st.variables())
    def test_success(self, variable_1, variable_2):
        variable_2.name = variable_1.name
        variable_2.assigment_type = variable_1.assigment_type

        assert self.check(variable_1, variable_2)

    @given(c_st.variables(), c_st.variables())
    def test_types_not_equals(self, variable_1, variable_2):
        assume(variable_1.assigment_type != variable_2.assigment_type)

        variable_2.name = variable_1.name

        assert not self.check(variable_1, variable_2)

    @given(c_st.variables(), c_st.variables())
    def test_no_assigment_type(self, variable_1, variable_2):
        variable_1.assigment_type = None

        variable_2.assigment_type = None
        variable_2.name = variable_1.name

        assert not self.check(variable_1, variable_2)


class TestAnnotationEquality:

    def check(self, variable_1, variable_2=None):
        checker = checkers.AnnotationEquality()
        return checker.check(variable_1, variable_2)

    @given(c_st.variables(), c_st.variables())
    def test_both_annotations_must_be_defined(self, variable_1, variable_2):
        assume(variable_1.annotation_type is None or
               variable_2.annotation_type is None)

        variable_2.name = variable_1.name

        assert not self.check(variable_1, variable_2)

    @given(c_st.variables(), c_st.variables())
    def test_annotations_are_identical(self, variable_1, variable_2):
        # TODO: configure c_st.variables instead of assume check
        assume(variable_1.annotation_type is not None)

        variable_2.name = variable_1.name
        variable_2.annotation_type = variable_1.annotation_type

        assert self.check(variable_1, variable_2)

    @pytest.mark.xfail
    @given(c_st.variables(), c_st.variables())
    def test_subtype(self, variable_1, variable_2):
        # TODO: configure c_st.variables instead of assume check
        assume(variable_2.annotation_type is not None)
        assume(variable_2.annotation_type not in types_for_tests.SPECIAL_TYPES)
        assume(not types_comparator.is_union(variable_2.annotation_type))

        class Child(variable_2.annotation_type):
            pass

        variable_1.name = variable_2.name
        variable_1.annotation_type = Child

        assert self.check(variable_1, variable_2)

    @given(c_st.variables(), c_st.variables())
    def test_parent_type(self, variable_1, variable_2):
        # TODO: configure c_st.variables instead of assume check
        assume(variable_1.annotation_type is not None)
        assume(variable_1.annotation_type not in types_for_tests.SPECIAL_TYPES)
        assume(not types_comparator.is_union(variable_1.annotation_type))

        class Child(variable_1.annotation_type):
            pass

        variable_2.name = variable_1.name
        variable_2.annotation_type = Child

        with pytest.raises(exceptions.TypeMistmatch):
            self.check(variable_1, variable_2)
