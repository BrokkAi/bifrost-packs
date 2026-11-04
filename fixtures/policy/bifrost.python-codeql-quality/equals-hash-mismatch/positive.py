class HashOnly:
    def __hash__(self):
        return 1


class HashAndEq:
    def __eq__(self, other):
        return True

    def __hash__(self):
        return 1


class EqualityBase:
    def __eq__(self, other):
        return True


class DerivedHash(EqualityBase):
    def __hash__(self):
        return 2
