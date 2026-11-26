class NameValidator:
    defaultexcludelist = ["return", "file", "print"]
    defaultdeletechars = set("~!@#$%^&*()-=+~|]}[{';: /?.>,<")

    def __init__(self, excludelist=None, deletechars=None):
        if excludelist:
            self.defaultexcludelist.extend(excludelist)
        if deletechars:
            self.defaultdeletechars.update(deletechars)


class Router:
    routes = {}

    def add(self, path, handler):
        self.routes.setdefault(path, handler)
