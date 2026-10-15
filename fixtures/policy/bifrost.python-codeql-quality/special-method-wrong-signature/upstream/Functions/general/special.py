# Source: github/codeql/python/ql/test/query-tests/Functions/general/special.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

#Special
class C(object):

    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass

    def __get__(self, *args):
        pass

from zope.interface import Interface

class I(Interface):
    pass

class M(I):

    def __setattr__(name, value):
        pass

    def __getitem__(name):
        pass
