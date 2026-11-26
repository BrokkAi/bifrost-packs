def milp(c, options=None):
    options = options or {}
    disp = options.pop("disp", False)
    options.setdefault("time_limit", 10)
    return c, disp


def shgo(func, minimizer_kwargs=None):
    minimizer_kwargs = minimizer_kwargs or {}
    minimizer_kwargs["jac"] = True
    return func


def request(url, headers=None):
    headers = headers or dict()
    headers.update({"Accept": "application/json"})
    return url, headers


def fit(x, solver_options=None):
    solver_options = solver_options if solver_options is not None else {}
    solver_options["maxiter"] = 100
    return x
