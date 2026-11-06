import os
from urllib.request import urlopen


def fetch():
    url = os.environ["FEED_URL"]
    urlopen(url)
