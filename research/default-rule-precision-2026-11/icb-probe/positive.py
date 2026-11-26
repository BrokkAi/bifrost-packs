def adjacent(a, b, out):
    if a:
        out.append(1)
    elif b:
        out.append(1)
    else:
        out.append(2)


def redundant_elif(kind):
    if kind == "a":
        return 1
    elif kind == "b":
        return 2
    else:
        return 2


def run_of_three(a, b, c, out):
    if a:
        out.discard(0)
    elif b:
        out.discard(0)
    elif c:
        out.discard(0)
    else:
        out.add(0)
