
class CoulsonError(Exception):
    pass


class CompareTypesError(CoulsonError):
    pass


class TypeAnnotationMismatch(CompareTypesError):

    def __init__(self, name, type, annotation, file, line):
        self.name = name
        self.type = type
        self.annotation = annotation
        self.file = file
        self.line = line

        super().__init__()

    def __str__(self):
        return (f'Type of value not equal to annotation: "{self.name}" in {self.file}:{self.line}\n'
                f'type: {self.type}\n'
                f'annotation: {self.annotation}')


class TypeMistmatch(CompareTypesError):

    def __init__(self, name, stored_type, stored_type_is_annotation, new_type, new_type_is_annotation, file, line):
        self.name = name
        self.stored_type = stored_type
        self.stored_type_is_annotation = stored_type_is_annotation
        self.new_type = new_type
        self.new_type_is_annotation = new_type_is_annotation
        self.file = file
        self.line = line
        super().__init__()

    def __str__(self):
        return (f'Type mismatch for vairable "{self.name}" in {self.file}:{self.line}\n'
                f'stored type: {self.stored_type}, is annotation: {self.stored_type_is_annotation}\n'
                f'new type: {self.new_type}, is annotation: {self.new_type_is_annotation}')
