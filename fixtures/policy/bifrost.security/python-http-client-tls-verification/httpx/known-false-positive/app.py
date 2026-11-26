import httpx


def own_transport(url):
    # Reported, although this client verifies: httpx uses the supplied
    # transport as given and verify= only configures the default one. The rule
    # can't prove what a transport expression evaluates to.
    return httpx.Client(verify=False, transport=httpx.HTTPTransport(verify=True)).get(url)
