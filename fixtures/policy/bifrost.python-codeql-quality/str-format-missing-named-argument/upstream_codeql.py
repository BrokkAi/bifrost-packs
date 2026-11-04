# Upstream source: github/codeql/python/ql/test/query-tests/Expressions/Formatting/test.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 4-4
named_format1 = "{name!r}, {0}"

# Excerpt from upstream lines 17-17
named_format1.format("Hello", world="World") # $ Alert[py/str-format/missing-named-argument] Alert[py/str-format/surplus-named-argument]

# Excerpt from upstream lines 20-20
named_format1.format(name="Hello", world="World") # $ Alert[py/str-format/missing-argument] Alert[py/str-format/surplus-named-argument]
