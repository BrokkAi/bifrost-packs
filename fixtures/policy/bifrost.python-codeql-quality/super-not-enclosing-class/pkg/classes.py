class Parent:
    def get(self, name):
        return name


class Target(Parent):
    def bad(self):
        return super(Other, self).get("x")

    def good(self):
        return super(Target, self).get("x")

class Other(Parent):
    def good(self):
        return super(Other, self).get("x")
