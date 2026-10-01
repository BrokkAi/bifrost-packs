import hashlib
import hmac
import os
import pickle


def restore_wrongly_authenticated_record(signed_bytes, supplied_mac, trusted_key):
    payload = os.environ["PICKLE_PAYLOAD"].encode("latin-1")
    expected_mac = hmac.digest(trusted_key, signed_bytes, "sha256")
    if not hmac.compare_digest(expected_mac, supplied_mac):
        raise ValueError("invalid record authentication")
    return pickle.loads(payload)
