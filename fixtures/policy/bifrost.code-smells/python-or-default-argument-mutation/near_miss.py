def copied(c, options=None):
    options = dict(options or {})
    options.pop("disp", None)
    return c


def merged(c, options=None, defaults=None):
    opts = {**(defaults or {}), **(options or {})}
    opts.pop("disp", None)
    return c


def read_only(c, options=None):
    options = options or {}
    return options.get("disp", False)


def walk(node, visited=None):
    visited = visited or set()
    visited.add(node)
    return visited


def memo_fib(n, memo=None):
    memo = memo or {}
    memo[n] = n
    return memo


def rebound_copy(c, options=None):
    options = options or {}
    options = options.copy()
    options.pop("disp", None)
    return c


def lookup_store(table, options=None):
    options = options or {}
    table[options.get("key")] = 1
    return table


def store_elsewhere(results, options=None):
    options = options or {}
    results["fit"] = run(**options)
    return results


def run(**kwargs):
    return kwargs


def bounded(x, options=None, lo=0, hi=1):
    options = options or {}
    return lo < x < hi and options.get("ok")


def conditional_copy(c, options=None):
    options = options.copy() if options is not None else {}
    options.pop("disp", None)
    return c


def read_into_other(settings, options=None):
    options = options or {}
    settings["x"] = options["x"]
    return settings


def fresh_kwargs(c, **kwargs):
    kwargs = kwargs or {}
    kwargs.pop("disp", None)
    return c


def fresh_prefixed(c, **solver_kwargs):
    solver_kwargs = solver_kwargs or {}
    solver_kwargs.pop("disp", None)
    return c


def key_read(settings, options=None):
    options = options or {}
    settings[options["name"]] = 1
    return settings
