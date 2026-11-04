# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/decorated_exports.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
import dotted

__all__ = ["foo", "bar", "baz", "not_defined"]


@dotted.decorator
def foo():
    pass

@undotted_decorator
def bar():
    pass

@not_imported.but_dotted
def baz():
    pass
