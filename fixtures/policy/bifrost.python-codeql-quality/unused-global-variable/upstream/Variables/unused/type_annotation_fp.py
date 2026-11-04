# Source: github/codeql/python/ql/test/query-tests/Variables/unused/type_annotation_fp.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
# FP Type annotation counts as redefinition
# See https://github.com/Semmle/ql/issues/2652

def type_annotation(x):
    foo = 5
    if x:
        foo : int
        do_stuff_with(foo)
    else:
        foo : float
        do_other_stuff_with(foo)

def type_annotation_fn():
    # False negative: the value of `bar` is never used, but this is masked by the presence of the type annotation.
    bar = 5
    bar : int
