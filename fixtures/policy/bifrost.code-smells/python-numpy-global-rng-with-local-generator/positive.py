import numpy as np


def make_noise(n_samples):
    rng = np.random.RandomState(seed=3)
    data = rng.randint(0, 10, size=n_samples)
    noise = np.random.rand(n_samples, n_samples)
    return data, noise


def bootstrap(x, random_state=None):
    idx = np.random.choice(len(x), size=len(x))
    return x[idx]


def shuffle_rows(x, rng=None):
    gen = np.random.default_rng(rng)
    np.random.shuffle(x)
    return gen.normal(size=3)


class Estimator:
    def fit(self, X, random_state=None):
        order = np.random.permutation(len(X))
        return X[order]
