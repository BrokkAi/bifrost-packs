import requests


def explicit_true(url):
    return requests.get(url, verify=True)


def ca_bundle(url):
    return requests.post(url, data={}, verify="/etc/ssl/certs/internal-ca.pem")


def default(url):
    return requests.get(url)


def from_settings(url, settings):
    # Not a literal: the value is not known here, so it is not reported.
    return requests.get(url, verify=settings.VERIFY)


def other_keyword(url):
    return requests.get(url, stream=False, allow_redirects=False)


def session_ok(url):
    with requests.Session() as s:
        return s.get(url, verify="/etc/ssl/certs/internal-ca.pem")


class Client:
    def get(self, url, verify=True):
        return url


def lookalike(url):
    # An application method named get with verify=False is not requests.
    return Client().get(url, verify=False)
