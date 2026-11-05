import sys
import urllib.request

from helpers import normalize


def fetch_wrapped():
    return urllib.request.urlopen(normalize(sys.argv[1])).read()
