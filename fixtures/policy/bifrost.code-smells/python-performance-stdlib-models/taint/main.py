import json
import pickle
import sys
import urllib.request


def a():
    return urllib.request.urlopen(json.loads(sys.argv[1]))


def b():
    return urllib.request.urlopen(json.loads(sys.argv[1], parse_float=float))


def c():
    return urllib.request.urlopen(pickle.loads(sys.argv[1]))
