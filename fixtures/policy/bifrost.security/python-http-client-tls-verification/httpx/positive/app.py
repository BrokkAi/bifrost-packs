import httpx


def fetch(url):
    return httpx.get(url, verify=False)


def send(url, token):
    return httpx.post(url, headers={"Authorization": token}, verify=False)


def streamed(url):
    with httpx.stream("GET", url, verify=False) as response:
        return response.read()


def client(url):
    with httpx.Client(verify=False, timeout=10) as c:
        return c.get(url)


async def async_client(url):
    async with httpx.AsyncClient(verify=False) as c:
        return await c.get(url)


def empty_mounts(url):
    # No mount matches, so the unverified default transport handles the URL.
    return httpx.Client(verify=False, mounts={}).get(url)


def proxied_transport(url):
    # With proxy=, httpx routes through a proxy transport built with verify=False.
    return httpx.Client(verify=False, transport=httpx.HTTPTransport(verify=True), proxy="http://proxy:8080").get(url)
