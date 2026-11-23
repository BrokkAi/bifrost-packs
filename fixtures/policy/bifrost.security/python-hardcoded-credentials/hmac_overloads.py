"""Positive and near-miss hmac.new call shapes."""
import hashlib
import hmac
import hmac as hmac_alias
from hmac import new as hmac_new

import requests


def positional_digestmod():
    return hmac.new(b"hardcoded-hmac-key-value", b"payload", "sha256")


def keyword_only_digestmod():
    return hmac.new(b"hardcoded-hmac-key-value", digestmod="sha256")


def keyword_key():
    return hmac.new(msg=b"payload", key=b"hardcoded-hmac-key-value", digestmod="sha256")


def local_key():
    """Pass the key through a local variable."""
    secret = b"hardcoded-hmac-key-value"
    return hmac.new(secret, b"payload", digestmod=hashlib.sha256)


def module_alias():
    return hmac_alias.new(b"hardcoded-hmac-key-value", b"payload", "sha256")


def imported_name():
    return hmac_new(b"hardcoded-hmac-key-value", b"payload", "sha256")


def short_key():
    return hmac.new(b"short", b"long-message-is-not-the-key", digestmod="sha256")


def long_keyword_message(key):
    return hmac.new(key, msg=b"long-message-is-not-the-key", digestmod="sha256")


def long_message_before_key(key):
    return hmac.new(msg=b"long-message-is-not-the-key", key=key, digestmod="sha256")


def long_digest_name(key):
    return hmac.new(key, b"payload", digestmod="long-digest-name-not-a-key")


def spread_arguments(arguments):
    return hmac.new(*arguments)


def unrelated_hash():
    return hashlib.new("long-algorithm-name", b"payload")


class Signer:
    def __init__(self, prefix):
        self.prefix = prefix

    def new(self, key, msg, digestmod):
        return self.prefix + key + msg + digestmod.encode()


def caller_defined_new():
    return Signer(b"v1:").new(b"hardcoded-hmac-key-value", b"payload", "sha256")


def third_party_call():
    return requests.get("https://example.com/long-url-literal")
