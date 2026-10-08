# Upstream source: github/codeql/python/ql/test/query-tests/Expressions/eq/expressions_test.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 44-47
#Using 'is' when should be using '=='
s = "Hello " + "World"
if "Hello World" is s: # $ Alert[py/comparison-using-is]
    print ("OK")

# Excerpt from upstream lines 49-52
#This is OK in CPython, but may not be portable
s = str(7)
if "7" is s:
    print ("OK")

# Excerpt from upstream lines 69-72
#Portable is comparisons
def f(arg):
    arg is ()
    arg is 0
