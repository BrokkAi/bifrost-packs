import urllib3
from urllib3 import PoolManager


def manager(url):
    http = urllib3.PoolManager(cert_reqs="CERT_NONE")
    return http.request("GET", url)


def short_name(url):
    return PoolManager(num_pools=4, cert_reqs="NONE").request("GET", url)


def no_hostname(url):
    return urllib3.PoolManager(assert_hostname=False).request("GET", url)


def proxy(proxy_url, url):
    return urllib3.ProxyManager(proxy_url, cert_reqs="CERT_NONE").request("GET", url)


def pool(host):
    return urllib3.HTTPSConnectionPool(host, 443, cert_reqs="CERT_NONE")


def helper(url):
    return urllib3.connection_from_url(url, assert_hostname=False)


def empty_fingerprint(url):
    # urllib3 skips an empty fingerprint, so nothing is pinned.
    return urllib3.PoolManager(cert_reqs="CERT_NONE", assert_fingerprint="").request("GET", url)


def optional_fingerprint(url, fingerprint=None):
    # A variable may hold None or "", which urllib3 skips.
    return urllib3.PoolManager(cert_reqs="CERT_NONE", assert_fingerprint=fingerprint).request("GET", url)
