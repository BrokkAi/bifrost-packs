# Upstream source: github/codeql/python/ql/test/query-tests/Expressions/general/expressions_test.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 63-67
    print ("Very surprising!")
    
#This is also OK
if s is None:
    print ("Also surprising")

# Excerpt from upstream lines 112-115
#Equals none

def x(arg):
    return arg == None # $ Alert[py/test-equals-none]
