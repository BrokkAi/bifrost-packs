def mixed(flag):
    if flag:
        return (1, 2)
    return (1, 2, 3)

def alias(flag):
    if flag:
        pair = (1, 2)
        return pair
    return (1, 2, 3)

def uniform(flag):
    if flag:
        return (1, 2)
    return (3, 4)

def annotated(flag) -> tuple:
    if flag:
        return (1, 2)
    return (1, 2, 3)
