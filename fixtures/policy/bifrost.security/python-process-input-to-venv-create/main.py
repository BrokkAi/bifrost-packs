import os
import sys
import venv
from venv import create


def create_from_argument():
    venv.create(sys.argv[1])


def create_from_environment():
    target = os.environ["BUILD_ENV_DIR"]
    create(target)


def create_with_clear():
    venv.create(sys.argv[1], False, True)


def create_with_keyword():
    venv.create(env_dir=os.environ["BUILD_ENV_DIR"])


def create_constant():
    venv.create(".venv")


def create_constant_with_input():
    name = sys.argv[1]
    venv.create(".venv", False, False, False, True), name
