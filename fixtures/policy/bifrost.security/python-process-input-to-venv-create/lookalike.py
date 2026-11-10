import sys


class LocalBuilder:
    def create(self, env_dir):
        return env_dir


def create_with_local_builder():
    target = sys.argv[1]
    venv = LocalBuilder()
    return venv.create(target)
