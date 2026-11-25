from urllib.request import urlopen

from django.http import HttpRequest, QueryDict


def status():
    # The request value is read but never reaches the URL.
    request = HttpRequest()
    request.GET.get("verbose")
    return urlopen("https://status.example.com/")


def health():
    # A QueryDict the application built is not request input.
    defaults = QueryDict("status=https://status.example.com/")
    return urlopen(defaults.get("status"))
