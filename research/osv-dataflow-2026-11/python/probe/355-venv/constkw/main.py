"""Research probe for BrokkAi/bifrost-packs#355: the `constkw` case."""
import os
import sys
import venv


def f():
    """Exercise the f case."""
    venv.create(".venv", prompt="build")
