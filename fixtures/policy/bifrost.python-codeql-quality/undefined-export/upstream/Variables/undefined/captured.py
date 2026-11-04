#!/usr/bin/python
# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/captured.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

def topLevel():
    foo = 3

    def bar():
        nonlocal foo
        print(foo)
        foo = 4

    bar()
    print(foo)

topLevel()
