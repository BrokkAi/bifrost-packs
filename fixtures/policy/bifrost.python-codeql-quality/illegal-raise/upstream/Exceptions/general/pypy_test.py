# Source: github/codeql/python/ql/test/query-tests/Exceptions/general/pypy_test.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

def test():
    class A(BaseException):
        class __metaclass__(type):
            def __getattribute__(self, name):
                if flag and name == '__bases__':
                    fail("someone read bases attr")
                else:
                    return type.__getattribute__(self, name)

    try:
        a = A()
        raise a
    except 42:
        #Some comment
        pass
    except A:
        #Another comment
        pass
