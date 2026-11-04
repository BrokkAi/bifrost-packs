class LocalBase:
    pass


def base_factory():
    return LocalBase


class MissingName(NoSuchBase):
    pass


class CallResult(base_factory()):
    pass


dynamic_base = base_factory()


class DynamicValue(dynamic_base):
    pass


class ResolvedLocal(LocalBase):
    pass


from base import ImportedBase


class ResolvedImported(ImportedBase):
    pass
