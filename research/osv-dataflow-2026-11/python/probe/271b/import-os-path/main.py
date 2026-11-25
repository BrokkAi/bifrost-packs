import os.path
import sys


def show():
    return os.path.expandvars(sys.argv[1])
