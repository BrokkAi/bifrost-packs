import os
from urllib.request import urlopen

from django.http import HttpRequest

DEFAULTS = {"command": "uptime"}


def uptime() -> int:
    # The request value is read but never reaches the command.
    request = HttpRequest()
    request.GET.get("verbose")
    return os.system("uptime")


def status() -> int:
    # `get` on a plain dict is not a request read.
    return os.system(DEFAULTS.get("command"))


def health() -> bytes:
    # The request value only selects between two constant URLs.
    request = HttpRequest()
    if request.GET.get("region") == "eu":
        return urlopen("https://eu.status.example.com/").read()
    return urlopen("https://status.example.com/").read()
