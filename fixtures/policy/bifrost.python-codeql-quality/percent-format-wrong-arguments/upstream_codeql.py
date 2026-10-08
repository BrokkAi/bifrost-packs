# Upstream source: github/codeql/python/ql/test/query-tests/Expressions/general/str_fmt_test.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 10-14
def wrong_arg_count_format(arg):
    print(u"%s %s" % (arg, arg, 0))
    format = u"%hd"
    args = (1, u'foo')
    print(format % args)

# Excerpt from upstream lines 17-19
def ok():
    # allowable length modifiers
    print(u"%hd %ld %Ld" % (1,2,3))

# Excerpt from upstream lines 27-28
    # a list is OK as an argument to %s
    print(u"%s is a list" % [1,2,3,4])
