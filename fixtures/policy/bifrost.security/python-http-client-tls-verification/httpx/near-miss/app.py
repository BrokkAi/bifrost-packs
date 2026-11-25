import ssl

import httpx


def default(url):
    return httpx.get(url)


def explicit_true(url):
    return httpx.get(url, verify=True)


def ca_bundle(url):
    return httpx.Client(verify="/etc/ssl/certs/internal-ca.pem").get(url)


def context(url):
    ctx = ssl.create_default_context()
    return httpx.Client(verify=ctx).get(url)


def from_settings(url, settings):
    return httpx.get(url, verify=settings.VERIFY)


def other_false(url):
    return httpx.get(url, follow_redirects=False)
