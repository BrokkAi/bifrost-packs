class Copied:
    excludes = ["return"]

    def __init__(self, extra):
        self.excludes = list(self.excludes)
        self.excludes.extend(extra)


class Immutable:
    excludes = ("return",)
    chars = frozenset("~!")

    def names(self):
        return self.excludes + ("x",)


class Registry:
    handlers = {}

    @classmethod
    def register(cls, name, fn):
        cls.handlers.setdefault(name, fn)


class Instance:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)


class Annotated:
    tags: list = []

    def tag(self, t):
        self.tags.append(t)


class Plugin:
    _instances = []

    def __init__(self):
        self._instances.append(self)
