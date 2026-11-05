import sys
from os.path import expandvars


def show():
    return expandvars(sys.argv[1])
