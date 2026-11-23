class Widget:
    def resize(self, width):
        old = self.width
        self.width = width
        return old


def main():
    widget = Widget()
    widget.width = 1
    return widget.resize(2)
