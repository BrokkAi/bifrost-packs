# Upstream source: github/codeql/python/ql/src/Lexical/OldOctalLiteral.py
# CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# Excerpt from upstream lines 1-10

#Easily misread as x = 15
x = 015

#The extra 'o' alerts the reader that this is an octal literal
y = 0o15

#If this is a byte sized value then a hexadecimal might be clearer
y = 0x0d

