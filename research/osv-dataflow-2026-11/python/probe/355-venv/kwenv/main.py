"""Research probe for BrokkAi/bifrost-packs#355: the `kwenv` case."""
import os
import sys
import venv


def f():
    """Exercise the f case."""
    venv.create(env_dir=sys.argv[1])
