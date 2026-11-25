"""Positive and near-miss cases for process input reaching venv.create (BrokkAi/bifrost-packs#355)."""
import os
import sys
import venv
from venv import create


def create_from_argument():
    """Exercise the create from argument case."""
    venv.create(sys.argv[1])


def create_from_environment():
    """Exercise the create from environment case."""
    target = os.environ["BUILD_ENV_DIR"]
    create(target)


def create_with_clear():
    """Exercise the create with clear case."""
    venv.create(sys.argv[1], False, True)


def create_with_keyword():
    """Exercise the create with keyword case."""
    venv.create(env_dir=os.environ["BUILD_ENV_DIR"])


def create_constant():
    """Exercise the create constant case."""
    venv.create(".venv")


def create_constant_with_input():
    """Exercise the create constant with input case."""
    name = sys.argv[1]
    venv.create(".venv", False, False, False, True), name
