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
