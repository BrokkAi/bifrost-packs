import requests
from requests import Session


def send_credentials(url, creds):
    return requests.post(url, data=creds, verify=False)


def fetch(url):
    return requests.get(url, verify=False)


def generic(url):
    return requests.request("DELETE", url, timeout=5, verify=False)


def session_call(url):
    s = requests.Session()
    return s.put(url, json={"a": 1}, verify=False)


def imported_session(url):
    return Session().get(url, params={"q": 1}, verify=False)
