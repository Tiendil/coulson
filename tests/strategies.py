
import typing
import string
import keyword

from hypothesis import assume
from hypothesis import strategies as st

from coulson import namespaces

from . import types_for_tests


# TODO: use python rules https://docs.python.org/3/reference/lexical_analysis.html#identifiers

HEAD_CHARACTERS = '_' + string.ascii_letters
TAIL_CHARACTERS = HEAD_CHARACTERS + string.digits


@st.composite
def random_variable_names(draw,
                          head=st.sampled_from(HEAD_CHARACTERS),
                          tail=st.text(alphabet=TAIL_CHARACTERS, min_size=0)):
    head_name = draw(head)
    tail_name = draw(tail)

    name = head_name + tail_name

    assume(not keyword.iskeyword(name))

    return name


variable_names = st.sampled_from(['self', 'cls']) | random_variable_names()


file_paths = st.text()
line_numbers = st.integers(min_value=1)


types = st.sampled_from(types_for_tests.TYPES)


def annotation_identity(draw, type):
    return type


def annotation_optional(draw, type):
    return typing.Optional[type]


def annotation_none(draw, type):
    return None


def annotation_union(draw, type, types=types):
    return typing.Union[type, draw(types)]


annotation_constructors = st.sampled_from([annotation_identity,
                                           annotation_optional,
                                           annotation_union,
                                           annotation_none])


# TODO: refactor to recursion annotations construction
@st.composite
def types_with_annotations(draw,
                           annotations=annotation_constructors,
                           types=types):
    type = draw(types)

    annotation = draw(annotations)(draw, type)

    return (type, annotation)


@st.composite
def variables(draw,
              names=variable_names,
              files=file_paths,
              lines=line_numbers,
              types_with_annotations=types_with_annotations()):

    type, annotation = draw(types_with_annotations)

    return namespaces.Variable(name=draw(names),
                               annotation_type=annotation,
                               assigment_type=type,
                               file=draw(files),
                               line=draw(lines))
