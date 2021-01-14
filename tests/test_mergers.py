
import random

from hypothesis import given, assume
from hypothesis import strategies as h_st

from coulson import mergers
from coulson import types_comparators

from . import strategies as c_st
from . import types_for_tests
from . import helpers


class TestSkipVariables:

    def merge(self, names, variable, new_type, is_annotation):
        merger = mergers.SkipVariables(names=names)
        return merger.merge(variable, new_type, is_annotation)

    @given(c_st.variables(), c_st.types, h_st.lists(c_st.variable_names, min_size=1), h_st.booleans())
    def test_success(self, variable, new_type, merger_names, is_annotation):

        variable.name = random.choice(merger_names)

        with helpers.not_changed(variable):
            assert self.merge(merger_names, variable, new_type, is_annotation)

    @given(c_st.variables(), c_st.types, h_st.lists(c_st.variable_names), h_st.booleans())
    def test_continue(self, variable, new_type, merger_names, is_annotation):
        assume(variable.name not in merger_names)

        with helpers.not_changed(variable):
            assert not self.merge(merger_names, variable, new_type, is_annotation)


class TestTypeDependency:

    def merge(self, variable, new_type, is_annotation):
        merger = mergers.TypeDependency()
        return merger.merge(variable, new_type, is_annotation)

    @given(c_st.variables(is_annotation=h_st.just(False)))
    def test_types_is_equal__not_annoted(self, variable):
        with helpers.not_changed(variable):
            assert self.merge(variable, variable.expected_type, False)

        with helpers.changed(variable):
            assert self.merge(variable, variable.expected_type, True)

        assert variable.is_annotation

    @given(c_st.variables(is_annotation=h_st.just(True)), h_st.booleans())
    def test_types_is_equal__already_annotated(self, variable, is_annotation):
        with helpers.not_changed(variable):
            assert self.merge(variable, variable.expected_type, is_annotation)

    @given(c_st.variables(), c_st.types, h_st.booleans())
    def test_types_not_equals(self, variable, new_type, is_annotation):
        assume(not types_comparators.is_subtype_or_equal(new_type, variable.expected_type))
        assume(not types_comparators.is_subtype_or_equal(variable.expected_type, new_type))

        with helpers.not_changed(variable):
            assert not self.merge(variable, new_type, is_annotation)

    @given(c_st.variables(is_annotation=h_st.just(False)), c_st.types_with_annotations())
    def test_new_type_is_subtype__real_type__not_annotated(self, variable, type_with_annotation):
        assume(type_with_annotation[0] is not type_with_annotation[1])

        # expected_type must be parent of new_type
        new_type, variable.expected_type = type_with_annotation

        with helpers.not_changed(variable):
            assert self.merge(variable, new_type, False)

    @given(c_st.variables(is_annotation=h_st.just(False)), c_st.types_with_annotations())
    def test_new_type_is_subtype__real_type__annotated(self, variable, type_with_annotation):
        assume(type_with_annotation[0] is not type_with_annotation[1])
        assume(type_with_annotation[0] not in types_for_tests.COMMON_TYPES)

        # expected_type must be parent of new_type
        new_type, variable.expected_type = type_with_annotation

        with helpers.not_changed(variable):
            assert not self.merge(variable, new_type, True)

    @given(c_st.variables(is_annotation=h_st.just(True)), c_st.types_with_annotations())
    def test_new_type_is_subtype__annotated_type(self, variable, type_with_annotation):
        assume(type_with_annotation[0] is not type_with_annotation[1])

        # expected_type must be parent of new_type
        new_type, variable.expected_type = type_with_annotation

        with helpers.not_changed(variable):
            assert self.merge(variable, new_type, False)

        with helpers.not_changed(variable):
            assert self.merge(variable, new_type, True)

    @given(c_st.variables(is_annotation=h_st.just(False)), c_st.types_with_annotations())
    def test_old_type_is_subtype__real_type__not_annotated(self, variable, type_with_annotation):
        assume(type_with_annotation[0] is not type_with_annotation[1])
        assume(type_with_annotation[0] not in types_for_tests.COMMON_TYPES)

        # expected_type must be parent of new_type
        variable.expected_type, new_type = type_with_annotation

        with helpers.not_changed(variable):
            assert not self.merge(variable, new_type, False)

    @given(c_st.variables(is_annotation=h_st.just(False)), c_st.types_with_annotations())
    def test_old_type_is_subtype__real_type__annotated(self, variable, type_with_annotation):
        assume(type_with_annotation[0] is not type_with_annotation[1])
        assume(type_with_annotation[0] not in types_for_tests.COMMON_TYPES)

        # expected_type must be parent of new_type
        variable.expected_type, new_type = type_with_annotation

        with helpers.changed(variable):
            assert self.merge(variable, new_type, True)

        assert variable.is_annotation
        assert variable.expected_type == new_type

    @given(c_st.variables(is_annotation=h_st.just(True)), c_st.types_with_annotations())
    def test_old_type_is_subtype__annotated_type(self, variable, type_with_annotation):
        assume(type_with_annotation[0] is not type_with_annotation[1])
        assume(type_with_annotation[0] not in types_for_tests.COMMON_TYPES)

        # expected_type must be parent of new_type
        variable.expected_type, new_type = type_with_annotation

        with helpers.not_changed(variable):
            assert not self.merge(variable, new_type, False)

        with helpers.not_changed(variable):
            assert not self.merge(variable, new_type, True)
