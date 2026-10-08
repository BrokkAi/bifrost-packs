def use_placeholder(choose):
    if choose:
        missing_placeholder = 1
    return missing_placeholder


def initialized_in_every_arm(choose):
    if choose:
        value = 1
    else:
        value = 2
    return value


def initialized_before_use(choose):
    value = 1
    if choose:
        value = 2
    return value
