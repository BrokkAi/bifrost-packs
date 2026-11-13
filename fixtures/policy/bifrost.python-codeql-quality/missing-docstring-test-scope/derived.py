from checks import Checks


class DerivedChecks(Checks):
    def verify_more(self):
        value = 2
        other = 2
        self.assertEqual(value, other)
