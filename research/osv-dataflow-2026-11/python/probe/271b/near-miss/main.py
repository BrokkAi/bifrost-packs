import os
import sys


def show():
    name = sys.argv[1]
    return os.path.expandvars("$HOME/.cache"), name
