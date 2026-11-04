# Source: github/codeql/python/ql/test/query-tests/Classes/should-be-context-manager/should_be_context_manager.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
#Should be context manager

class MegaDel(object): # $ Alert

    def __del__(self):
        a = self.x + self.y
        if a:
            print(a)
        if sys._getframe().f_lineno > 100:
            print("Hello")
        sum = 0
        for a in range(100):
            sum += a
        print(sum)

class MiniDel(object): # $ Alert

    def close(self):
        pass

    def __del__(self):
        self.close()