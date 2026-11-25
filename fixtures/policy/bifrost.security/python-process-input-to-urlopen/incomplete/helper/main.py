import sys
import urllib.request

from links import normalize


def fetch_normalized():
    return urllib.request.urlopen(normalize(sys.argv[1]))
