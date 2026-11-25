import sys
from urllib.request import urlopen


def fetch():
    urlopen(sys.argv[1], None, 5)
