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
