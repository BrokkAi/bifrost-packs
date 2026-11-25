import os
import sys
import urllib.request
from urllib.request import urlopen


def fetch_argument():
    return urllib.request.urlopen(sys.argv[1])


def fetch_environment():
    url = os.environ["FEED_URL"]
    return urlopen(url)


def fetch_positional_timeout():
    return urlopen(sys.argv[1], None, 5)


def fetch_constant():
    return urllib.request.urlopen("https://example.invalid/feed")


def fetch_constant_with_input():
    label = sys.argv[1]
    return urlopen("https://example.invalid/feed"), label
