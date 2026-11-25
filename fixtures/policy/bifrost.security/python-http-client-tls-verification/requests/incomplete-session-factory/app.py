import requests


def factory_session(url):
    # requests.session() binds, but its declared Session result does not yet
    # give the receiver of s.request an exact type, so the run stays
    # inconclusive rather than clean.
    s = requests.session()
    return s.request("GET", url, verify=False)
