import pytest
from unittest import TestCase as Base


class Checks(Base):
    def verify(self):
        value = 1
        other = 1
        self.assertEqual(value, other)


def test_marker():
    marker = pytest.mark
    name = "slow"
    assert getattr(marker, name)


def build_marker():
    marker = pytest.mark
    name = "slow"
    return getattr(marker, name)
