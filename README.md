# Coulson

Checks types of variables in runtime on every change of variable value.

Tracks type inconsistency on base of variable name and domain (module) in which it uses.

Will raise an exception if see something like that:

``` python
def my_function():
    x = 666

    # other code

    x = '666' # <- raise here

    return x
```

# Current state

Very early prototype: very slow, a lot of TODOs in code, simplest types checking.

But it is working.

# Example

More usage examples you can see in tests.

``` python
    import os

    from coulson import tracers, mergers, namespaces

    PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

    spaces = [namespaces.Namespace('my_project_django_models',
                                   filter=namespaces.Chained([namespaces.ModulePath(PROJECT_DIR),
                                                              namespaces.ModulePathRE(r'models\.py')]),
                                   mergers=[mergers.SkipVariables(['self',
                                                                   'data',
                                                                   'account']),
                                            mergers.TypeDependency()]),

              namespaces.Namespace('my_project_django_forms',
                                   filter=namespaces.Chained([namespaces.ModulePath(PROJECT_DIR),
                                                              namespaces.ModulePathRE(r'forms\.py')]),
                                   mergers=[mergers.SkipVariables(['self',
                                                                   'label',
                                                                   'group']),
                                            mergers.TypeDependency()]),

              namespaces.Namespace('my_project',
                                   filter=namespaces.ModulePath(PROJECT_DIR),
                                   mergers=[mergers.SkipVariables(['self',
                                                                   'name',
                                                                   'base_value']),
                                            mergers.TypeDependency()])]

    tracer = tracers.Tracer(spaces)

    tracer.start_tracing()

    # or
    #
    # with tracer.trace():
    #    do smth
    #    pass
```
