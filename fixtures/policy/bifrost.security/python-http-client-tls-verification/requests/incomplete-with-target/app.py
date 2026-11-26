import requests


def with_session(url):
    # Reported, but the `as s` target leaves the receiver lookup open, so the
    # run is inconclusive rather than complete.
    with requests.Session() as s:
        return s.head(url, verify=False)
