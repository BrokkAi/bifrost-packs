import os
from urllib.request import urlopen

from django.http import HttpRequest, HttpResponse


def ping(request: HttpRequest) -> HttpResponse:
    # A view parameter: reported once bifrost-dev#14566 binds it.
    host = request.GET.get("host")
    return HttpResponse(str(os.system("ping -c 1 " + host)))


def replay() -> int:
    request = HttpRequest()
    names = request.POST.getlist("name")
    return os.system("tar czf out.tgz " + " ".join(names))


def fetch():
    request = HttpRequest()
    feed = request.GET.get("feed")
    return urlopen(feed)
