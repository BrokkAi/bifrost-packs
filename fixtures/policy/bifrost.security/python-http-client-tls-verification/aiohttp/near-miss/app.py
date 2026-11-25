import ssl

import aiohttp


async def default(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def context(url):
    ctx = ssl.create_default_context()
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=ctx) as response:
            return response.status


def connector_default():
    return aiohttp.TCPConnector(ssl=True)


async def no_redirects(url):
    async with aiohttp.request("GET", url, allow_redirects=False) as response:
        return response.status
