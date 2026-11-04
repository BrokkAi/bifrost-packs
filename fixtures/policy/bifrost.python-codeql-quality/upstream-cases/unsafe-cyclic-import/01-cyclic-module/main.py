# Source: github/codeql/python/ql/test/query-tests/Imports/cyclic-module/main.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

a = 1
b = 2

if __name__ == '__main__':
    import module9
    print(module9.y)
