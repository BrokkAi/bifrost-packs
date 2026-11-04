class Base:
    def __init__(self):
        self.shadow = 1


class Derived(Base):
    def shadow(self):
        return 1
