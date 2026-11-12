"""Research probe for BrokkAi/bifrost-packs#355: the `pos` case."""
import os
import sys
import venv


def f():
    """Exercise the f case."""
    venv.create(sys.argv[1])
