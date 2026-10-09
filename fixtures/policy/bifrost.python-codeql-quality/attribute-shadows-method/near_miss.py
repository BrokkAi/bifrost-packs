class BaseOwn:
    def __init__(self):
        self.own = 1

    def own(self):
        return 1


class DerivedOwn(BaseOwn):
    def own(self):
        return 2


class BaseProperty:
    def __init__(self):
        self.value = 1


class DerivedProperty(BaseProperty):
    @property
    def value(self):
        return 1

    @value.setter
    def value(self, new_value):
        pass
