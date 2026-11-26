import numpy as np

n_samples = 20
seed = np.random.RandomState(seed=3)
X_true = seed.randint(0, 20, 2 * n_samples).astype(float)
noise = np.random.rand(n_samples, n_samples)
