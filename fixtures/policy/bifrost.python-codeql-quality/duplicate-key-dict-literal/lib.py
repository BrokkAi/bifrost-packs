def duplicate():
    return {"a": 1, "a": 2}  # positive: second key overwrites first


def distinct():
    return {"a": 1, "b": 2}  # near miss: distinct keys


def duplicate_after_decoding():
    return {"same": 0, "s\x61me": 1}  # positive: equal decoded keys
