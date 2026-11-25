import aiohttp


async def post(url, creds):
    session = aiohttp.ClientSession()
    async with session.post(url, data=creds, verify_ssl=False) as response:
        return response.status


def connector():
    return aiohttp.TCPConnector(ssl=False, limit=10)


async def one_shot(url):
    async with aiohttp.request("GET", url, ssl=False) as response:
        return await response.read()


def get_call(url):
    session = aiohttp.ClientSession()
    return session.get(url, ssl=False)


async def websocket(url):
    session = aiohttp.ClientSession()
    return await session.ws_connect(url, verify_ssl=False)
