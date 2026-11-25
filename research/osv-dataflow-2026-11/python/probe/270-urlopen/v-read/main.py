import sys
from urllib.request import urlopen


def fetch():
    return urlopen(sys.argv[1]).read()
