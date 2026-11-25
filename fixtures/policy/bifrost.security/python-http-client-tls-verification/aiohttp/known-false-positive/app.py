import aiohttp


async def pinned_connector(url, digest):
    # Reported, although the connector's Fingerprint is still checked under a
    # request-level ssl=False. The rule can't prove the connector's identity.
    async with aiohttp.request(
        "GET", url, ssl=False, connector=aiohttp.TCPConnector(ssl=aiohttp.Fingerprint(digest))
    ) as response:
        return response.status
