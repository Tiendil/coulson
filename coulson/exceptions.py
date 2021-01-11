

class TypeMistmatch(Exception):

    def __init__(self, stored_variable, current_variable):
        message = ('Type mismatch\n'
                   f'stored variable: {stored_variable}\n'
                   f'current variable: {current_variable}')

        super().__init__(message)
