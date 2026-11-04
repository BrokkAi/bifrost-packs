class Useless:
    def run(self):
        return 1

class Useful:
    def first(self):
        return 1

    def second(self):
        return 2

class Stateful:
    def run(self):
        self.value = 1
        return self.value
