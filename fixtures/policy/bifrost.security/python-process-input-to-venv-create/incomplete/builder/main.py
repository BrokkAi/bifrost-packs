import sys
import venv


def create_with_builder():
    venv.EnvBuilder(with_pip=True).create(sys.argv[1])
