from positive import Base, Derived
from near_miss import BaseOwn, DerivedOwn, BaseProperty, DerivedProperty


def build():
    return Base, Derived, BaseOwn, DerivedOwn, BaseProperty, DerivedProperty
