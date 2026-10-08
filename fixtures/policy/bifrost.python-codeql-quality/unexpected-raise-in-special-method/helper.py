class Bad:
    def __getitem__(self, key):
        raise ValueError()


class Good:
    def __getitem__(self, key):
        raise KeyError()


class CallOnly:
    def __getitem__(self, key):
        error = ValueError()
        return error
