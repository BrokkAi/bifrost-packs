import os
import sys
import urllib.request
from urllib.request import urlopen


def fetch_argv():
    return urllib.request.urlopen(sys.argv[1]).read()


def fetch_env():
    url = os.environ["FEED_URL"]
    return urlopen(url, timeout=5).read()
