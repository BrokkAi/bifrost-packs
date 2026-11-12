"""Near miss: a local class whose create() method receives the input."""
import sys


class LocalBuilder:
    """Records requested directories instead of creating environments."""

    def __init__(self):
        self.requested = []

    def create(self, env_dir):
        """Record env_dir and return it."""
        self.requested.append(env_dir)
        return env_dir


def create_with_local_builder():
    """Exercise the create with local builder case."""
    target = sys.argv[1]
    venv = LocalBuilder()
    return venv.create(target)
