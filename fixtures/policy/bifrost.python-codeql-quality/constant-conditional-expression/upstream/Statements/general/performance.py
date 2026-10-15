# Source: github/codeql/python/ql/test/query-tests/Statements/general/performance.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

#String concat in loop
def y(seq):
    y_accum = ''
    for s in seq:
        y_accum += s


def z(seq):
    z_accum = ''
    for s in seq:
        z_accum = z_accum + s
