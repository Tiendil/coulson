import typing


class AnnotatedClassVars:
    x: typing.Union[str, type(NotImplemented)] = NotImplemented


class AnnotatedClassVarsChild(AnnotatedClassVars):
    x = 'some value'
