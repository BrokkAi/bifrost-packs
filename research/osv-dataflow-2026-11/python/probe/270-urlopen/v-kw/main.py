import sys
from urllib.request import urlopen


def fetch():
    urlopen(sys.argv[1], timeout=5)
