import re

UNSAFE = re.compile("(www|beta).example.com/")
SAFE = re.compile(r"(www|beta)\.example\.com/")


def route(host):
    return UNSAFE.match(host), SAFE.match(host)
