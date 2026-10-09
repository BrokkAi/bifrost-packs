class ValueEquality:
    def __eq__(self, other):
        return True


class IdentityOnly:
    pass


def check():
    value = ValueEquality() is ValueEquality()
    negated = ValueEquality() is not ValueEquality()
    identity = IdentityOnly() is IdentityOnly()
    mixed = ValueEquality() is IdentityOnly()
    sentinel = object() is None
    return value, negated, identity, mixed, sentinel
