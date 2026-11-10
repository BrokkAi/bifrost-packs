import os
import sys
import venv


def f():
    venv.create(env_dir=sys.argv[1])
