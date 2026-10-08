# Upstream source: github/codeql/python/ql/test/query-tests/Expressions/general/expressions_test.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 1-9
#encoding: utf-8
def dup_key():
    return { 1: -1, # $ Alert[py/duplicate-key-dict-literal]
             1: -2,
             u'a' : u'A', # $ Alert[py/duplicate-key-dict-literal]
             u'a' : u'B'
            }

def simple_func(*args, **kwrgs): pass

# Excerpt from upstream lines 211-217
def not_dup_key():
    return { u'a' : 0,
             b'a' : 0,
            u"😄" : 1,
            u"😅" : 2,
            u"😆" : 3
            }
