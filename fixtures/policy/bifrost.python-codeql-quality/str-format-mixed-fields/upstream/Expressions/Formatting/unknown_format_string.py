# Source: github/codeql/python/ql/test/query-tests/Expressions/Formatting/unknown_format_string.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
# FP Reported in https://github.com/github/codeql/issues/2650

def possibly_unknown_format_string1(x):
    user_specified = unknown_function()
    if user_specified:
        fmt = user_specified
    else:
        fmt = "{a}"
    return fmt.format(a=1,b=2) # $ Alert[py/str-format/surplus-named-argument]

def possibly_unknown_format_string2(x):
    user_specified = input()
    if user_specified:
        fmt = user_specified
    else:
        fmt = "{a}"
    return fmt.format(a=1,b=2) # $ Alert[py/str-format/surplus-named-argument]


def possibly_unknown_format_string3(x):
    if unknown_function():
        fmt = input()
    else:
        fmt = "{a}"
    return fmt.format(a=1,b=2) # $ Alert[py/str-format/surplus-named-argument]
