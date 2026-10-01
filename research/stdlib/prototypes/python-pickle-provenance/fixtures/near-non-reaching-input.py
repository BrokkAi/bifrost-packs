import os
import pickle


def restore_constant_record():
    ignored_payload = os.environ["PICKLE_PAYLOAD"].encode("latin-1")
    return pickle.loads(b"\x80\x04N.")
