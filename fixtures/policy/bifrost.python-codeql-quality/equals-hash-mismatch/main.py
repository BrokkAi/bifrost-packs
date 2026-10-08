from positive import HashOnly, HashAndEq, EqualityBase, DerivedHash
from near_miss import EqOnly


def build():
    return HashOnly, HashAndEq, EqualityBase, DerivedHash, EqOnly
