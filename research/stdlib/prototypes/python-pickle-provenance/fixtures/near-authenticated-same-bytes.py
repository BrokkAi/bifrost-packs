import hashlib
import hmac
import pickle


def restore_authenticated_record(raw, supplied_mac, trusted_key):
    expected_mac = hmac.digest(trusted_key, raw, "sha256")
    if not hmac.compare_digest(expected_mac, supplied_mac):
        raise ValueError("invalid record authentication")
    return pickle.loads(raw)
