import sys
import urllib.request


def fetch_constant():
    return urllib.request.urlopen("https://example.invalid/feed")


def urlopen(url):
    return url


def local_lookalike():
    return urlopen(sys.argv[1])
