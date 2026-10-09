# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/unknown_import.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

from who_knows_what import *

#Anything could be imported from who_knows_what
#So we have to assume the following could be defined
a
b
c
