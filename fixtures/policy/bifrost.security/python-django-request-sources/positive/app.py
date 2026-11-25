from urllib.request import urlopen

from django.http import HttpRequest, HttpResponse


def feed(request: HttpRequest) -> HttpResponse:
    # A view parameter: reported once bifrost-dev#14566 binds it.
    return HttpResponse(urlopen(request.GET.get("url")))


def replay():
    request = HttpRequest()
    target = request.GET.get("target")
    return urlopen(target)


def callback():
    request = HttpRequest()
    hooks = request.POST.getlist("hook")
    return urlopen(hooks[0])
