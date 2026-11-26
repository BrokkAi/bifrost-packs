def bayesfactor_binom(k, n, p=0.5):
    assert 0 < p < 1, "p must be between 0 and 1."
    assert k <= n, "k must be <= n."
    return k / n


def correlation(x, y, method="pearson"):
    assert method in ["pearson", "spearman"], "unknown method"
    assert len(x) == len(y)
    return method


class Test:
    def __init__(self, alpha):
        assert alpha > 0, "alpha must be positive"
        self.alpha = alpha
