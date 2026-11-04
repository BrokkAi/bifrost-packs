# Source: github/codeql/python/ql/test/query-tests/Variables/unused_local_nonlocal/variables_test.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

# FPs involving nonlocal

def nonlocal_fp():
    test = False
    def set_test():
        nonlocal test
        test = True
    set_test()
    if test:
        print("Test is set.")

nonlocal_fp()

def nonlocal_fp2():
    test = False

    def set_test():
        nonlocal test
        test = True
    set_test()
    result = 5
    if not test:
        return
    return result

def not_fp():
    test = False
    def nonlocal_test():
        nonlocal test
    def set_test():
        test = True # $ Alert
    nonlocal_test()
    set_test()
    if test:
        print("Test is set.")
