# Upstream source: github/codeql/python/ql/test/query-tests/Expressions/Formatting/test.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 5-5
explicit_format1 = "{0}, {1}"

# Excerpt from upstream lines 23-23
explicit_format1.format("Hello") # $ Alert[py/str-format/missing-argument]

# Excerpt from upstream lines 29-29
explicit_format1.format("Hello", "World", "Extra") # $ Alert[py/str-format/surplus-argument]
