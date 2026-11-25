import numpy as np
import random


def all_local(n, random_state=0):
    rng = np.random.default_rng(random_state)
    return rng.normal(size=n), rng.integers(0, 5)


def global_only(n):
    return np.random.rand(n)


def seeded_global(n, seed=0):
    np.random.seed(seed)
    return np.random.rand(n)


def stdlib_random(items, rng=None):
    gen = np.random.default_rng(rng)
    random.shuffle(items)
    return gen.integers(0, 5)


class Sampler:
    def __init__(self, random_state=None):
        self.random_state = random_state

    def other(self):
        return np.random.rand(3)
