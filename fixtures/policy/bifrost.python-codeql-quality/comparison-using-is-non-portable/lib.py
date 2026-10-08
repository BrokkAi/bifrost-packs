class ValueEquality:
    def __eq__(self, other):
        return True


class IdentityOnly:
    pass


def check():
    string = "a" is ValueEquality()
    small_integer = 7 is ValueEquality()
    negative_small_integer = -5 is ValueEquality()
    inverse = ValueEquality() is not "8"
    zero = 0 is ValueEquality()
    empty_string = "" is ValueEquality()
    long_string = "several characters" is ValueEquality()
    large_integer = 257 is ValueEquality()
    below_negative_range = -6 is ValueEquality()
    identity_only = 1 is IdentityOnly()
    return (string, small_integer, negative_small_integer, inverse, zero,
            empty_string, long_string, large_integer, below_negative_range,
            identity_only)
