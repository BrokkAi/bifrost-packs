import sys
from urllib.request import urlopen


def fetch_body():
    return urlopen(sys.argv[1]).read()
