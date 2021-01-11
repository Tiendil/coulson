
import random
import string
import keyword

from hypothesis import given, assume
from hypothesis import strategies as st

from coulson import checkers
from coulson import namespaces


# TODO: use python rules https://docs.python.org/3/reference/lexical_analysis.html#identifiers
variable_names = st.text(alphabet=string.ascii_lowercase + '_' + string.digits,
                         min_size=1).filter(lambda x: (x.isidentifier() and
                                                       not keyword.iskeyword(x))) | st.sampled_from(["master"])

annotation_type = st.none()
assigment_type = st.none()
file_path = st.text()
line_number = st.integers(min_value=1)


@st.composite
def variables(draw,
              name=variable_names,
              annotation=annotation_type,
              assigment=assigment_type,
              file=file_path,
              line=line_number):
    return namespaces.Variable(name=draw(name),
                               annotation_type=draw(annotation),
                               assigment_type=draw(assigment),
                               file=draw(file),
                               line=draw(line))


class TestSkipVariables:

    @given(variables(), st.lists(variable_names))
    def test_skipped(self, variable, checker_names):
        checker_names.append(variable.name)
        random.shuffle(checker_names)

        checker = checkers.SkipVariables(names=checker_names)

        assert checker.check(variable, variable)

    @given(variables(), st.lists(variable_names))
    def test_not_skipped(self, variable, checker_names):
        assume(variable.name not in checker_names)

        checker = checkers.SkipVariables(names=checker_names)

        assert not checker.check(variable, variable)
