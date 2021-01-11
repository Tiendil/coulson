
import copy
import random
import string
import keyword

import pytest

from hypothesis import given, assume
from hypothesis import strategies as st

from coulson import checkers
from coulson import namespaces


# TODO: use python rules https://docs.python.org/3/reference/lexical_analysis.html#identifiers
variable_names = st.text(alphabet=string.ascii_lowercase + '_' + string.digits,
                         min_size=1).filter(lambda x: (x.isidentifier() and
                                                       not keyword.iskeyword(x))) | st.sampled_from(['self', 'cls'])

annotation_type = st.none()
assigment_type = st.none()
file_path = st.text()
line_number = st.integers(min_value=1)


@st.composite
def variables(draw):
    return namespaces.Variable(name=draw(variable_names),
                               annotation_type=draw(annotation_type),
                               assigment_type=draw(assigment_type),
                               file=draw(file_path),
                               line=draw(line_number))


class TestSkipVariables:

    def check(self, names, variable_1, variable_2=None):
        checker = checkers.SkipVariables(names=names)

        if variable_2 is None:
            variable_2 = copy.deepcopy(variable_1)

        return checker.check(variable_1, variable_2)

    @given(variables(), variables(), st.lists(variable_names))
    def test_names_integrity(self, variable_1, variable_2, checker_names):
        assume(variable_1.name != variable_2.name)

        with pytest.raises(ValueError):
            assert self.check(checker_names, variable_1, variable_2)

    @given(variables(), st.lists(variable_names, min_size=1))
    def test_success(self, variable, checker_names):

        variable.name = random.choice(checker_names)

        assert self.check(checker_names, variable)

    @given(variables(), st.lists(variable_names))
    def test_continue(self, variable, checker_names):
        assume(variable.name not in checker_names)

        assert not self.check(checker_names, variable)
