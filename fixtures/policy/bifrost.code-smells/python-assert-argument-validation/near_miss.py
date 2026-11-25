def explicit(p):
    if not 0 < p < 1:
        raise ValueError("p must be between 0 and 1.")
    return p


def _private_helper(k, n):
    assert k <= n
    return k


def internal_state(values):
    total = sum(values)
    assert total >= 0
    return total


def type_narrowing(node):
    assert node is not None
    assert isinstance(node, dict)
    return node


class Model:
    def predict(self, x):
        assert self.fitted, "call fit first"
        assert self.n_features > 0
        return x


def rebound(p):
    p = float(p)
    assert p > 0
    return p


def outer(graph):
    def _recurse(b, v):
        assert b == v
        return b

    return _recurse(graph, graph)


def assert_graphs_equal(g1, g2):
    assert g1 == g2


def message_only(values, request_id):
    result = sum(values)
    assert result >= 0, request_id
    return result
