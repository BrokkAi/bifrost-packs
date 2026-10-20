# Source: github/codeql/python/ql/test/query-tests/Classes/conflicting/test.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.


#Conflicting attributes in base classes

class Common(object):
    ok1 = None

    def ok2(self):
        return None

class CB1(Common):
    attr = 1

    def meth(self):
        pass


class CB2(Common):

    attr = (x, y)

    def meth(self):
        return 0


class Conflict(CB1, CB2):
    pass

class Override1(Common):

    def ok2(self):
        return 1

class Override2(Common):

    def ok2(self):
        return 2

class OK1(Override1, Override2):

    def ok2(self):
        return 3


class Override3(Override2):
    pass

class OK2(Override1, Override3):

    def ok2(self):
        return 4
