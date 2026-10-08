def constants(value):
    scalar = 1 == 1  # positive: scalar constants
    tuple_expression = (1, "a" + "b", "c" "d", not False, ~1) == (1, "ab", "cd", True, -2)  # positive: tuple, string concat, and unary constants
    one_constant = value == 1  # near miss: only one operand is constant
    computed = (1 + 2) == 3  # known gap: general arithmetic is not folded
    assert 9 == 9  # near miss: direct assert test
    return scalar, tuple_expression, one_constant, computed


def variable_comparison(value):
    return value == 1
