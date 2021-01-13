
# TODOs

- support older python versions
- say thanks to typeguard (for inspiration)
- try https://pypi.org/project/Faker/
- try https://hypofuzz.com/
- try https://github.com/Teemu/pytest-sugar/
- rewrite exceptions.py
- it simce, that trace function called before execution of opcode, so we can check types only on next call. As a result, line numbers will be incorret for detected types mismatch.

# Qustions

- How to work with optional (None) types?
- How to work with self, class, and other variables with the same behaviour?
- How to work with closures?
- How to check generic types like dict[Key, Value]? Deduce Key, Values types with help of introspection of each step (too expensive)?
