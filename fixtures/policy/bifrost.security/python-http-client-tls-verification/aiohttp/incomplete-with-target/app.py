import aiohttp


# Both calls are reported, but the `as session` target leaves the receiver
# lookup open, so the run is inconclusive rather than complete.
async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as response:
            return await response.text()


async def websocket(url):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url, ssl=False) as ws:
            return await ws.receive()
