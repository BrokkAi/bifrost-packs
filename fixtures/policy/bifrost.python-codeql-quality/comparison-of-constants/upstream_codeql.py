# Upstream source: github/codeql/python/ql/test/query-tests/Expressions/general/compare.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 2-13
#OK
a = b = 1
a == b
a.x == b.x

#Same variables
a == a # $ Alert[py/comparison-of-identical-expressions]
a.x == a.x # $ Alert[py/comparison-of-identical-expressions]

#Compare constants
1 == 1 # $ Alert[py/comparison-of-constants]
1 == 2 # $ Alert[py/comparison-of-constants]

# Excerpt from upstream lines 25-26
#Compare constants in assert -- ok
assert(1 == 1)
