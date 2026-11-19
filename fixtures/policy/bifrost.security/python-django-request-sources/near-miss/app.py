import os
from urllib.request import urlopen

from django.http import HttpRequest, QueryDict

DEFAULTS = {"command": "uptime"}


def uptime() -> int:
    # The request value is read but never reaches the command.
    request = HttpRequest()
    request.GET.get("verbose")
    return os.system("uptime")


def status() -> int:
    # `get` on a plain dict is not a request read.
    return os.system(DEFAULTS.get("command"))


def health():
    # A QueryDict the application built is not request input.
    defaults = QueryDict("status=https://status.example.com/")
    return urlopen(defaults.get("status"))
