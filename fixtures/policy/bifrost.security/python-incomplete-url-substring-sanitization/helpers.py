import urllib.parse


def unsafe_prefix(url):
    return url.startswith("example.com")


def unsafe_suffix(url):
    return url.endswith("example.com")


def safe_suffix(url):
    return url.endswith(".example.com")


def unsafe_substring(url):
    return "example.com" in url


def safe_scheme_prefix(url):
    return url.startswith("https://example.com/")


def safe_parsed_hostname(url):
    return urllib.parse.urlparse(url).hostname == "example.com"


def unrelated_membership(url):
    return url in "example.com"
