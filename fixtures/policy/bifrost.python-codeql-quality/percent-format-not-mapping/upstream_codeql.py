# Upstream source: github/codeql/python/ql/test/query-tests/Expressions/general/str_fmt_test.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 3-5
def expected_mapping_for_fmt_string():
    x = [ u'list', u'not', u'mapping' ]
    print (u"%(name)s" % x)

# Excerpt from upstream lines 27-28
    # a list is OK as an argument to %s
    print(u"%s is a list" % [1,2,3,4])
