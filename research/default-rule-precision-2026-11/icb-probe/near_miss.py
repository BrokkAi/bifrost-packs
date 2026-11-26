def ladder(name, only_binary, no_binary):
    result = {"binary", "source"}
    if name in only_binary:
        result.discard("source")
    elif name in no_binary:
        result.discard("binary")
    elif ":all:" in only_binary:
        result.discard("source")
    elif ":all:" in no_binary:
        result.discard("binary")
    return frozenset(result)


def guards(prefix, common):
    if not prefix:
        return False
    elif common is None:
        return None
    elif prefix != common:
        return False
    return True


def fallback(kind, value):
    if kind == "text":
        data = value
    elif kind == "file":
        data = value.read()
    elif kind == "none":
        data = None
    else:
        data = value
    return data
