import urllib3


def required(url):
    return urllib3.PoolManager(cert_reqs="CERT_REQUIRED").request("GET", url)


def default(url):
    return urllib3.PoolManager().request("GET", url)


def pinned_hostname(host):
    return urllib3.HTTPSConnectionPool(host, 443, assert_hostname="internal.example")


def ca_certs(url):
    return urllib3.PoolManager(ca_certs="/etc/ssl/certs/internal-ca.pem").request("GET", url)


def from_settings(url, settings):
    return urllib3.PoolManager(cert_reqs=settings.CERT_REQS).request("GET", url)


def fingerprint_pinned(url):
    # assert_fingerprint pins the server certificate even with CERT_NONE.
    pin = "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99"
    return urllib3.PoolManager(cert_reqs="CERT_NONE", assert_fingerprint=pin).request("GET", url)
