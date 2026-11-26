import numpy as np


def make_rng(seed):
    return np.random.default_rng(seed)


noise = np.random.rand(3)
