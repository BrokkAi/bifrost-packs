class DirectBase:
    def __init__(this):
        receiver = this
        receiver.value = 0

class DirectShadowedChild(DirectBase):
    def value(self):
        return 1

class Root:
    def __init__(self):
        self.transitive = 0

class Middle(Root):
    pass

class TransitiveShadowed(Middle):
    def transitive(self):
        return 1

class DefinedBase:
    def __init__(self):
        self.same = 0
    def same(self):
        return 0

class DefinedShadowedChild(DefinedBase):
    def same(self):
        return 1

class PropertyBase:
    def __init__(self):
        self.item = 0

class SettableShadowedChild(PropertyBase):
    @property
    def item(self):
        return self._item
    @item.setter
    def item(self, value):
        self._item = value

class SetterBase:
    def __init__(self):
        self.other = 0

class SetterShadowedChild(SetterBase):
    @unrelated.setter
    def other(self, value):
        pass

class ReadOnlyShadowedChild(PropertyBase):
    @property
    def item(self):
        return 1
