import sys


def urlopen(url):
    return url


def local_lookalike():
    return urlopen(sys.argv[1])
