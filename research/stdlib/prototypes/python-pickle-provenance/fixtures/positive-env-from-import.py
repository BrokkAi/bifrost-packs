import os
from pickle import loads as decode_pickle


def restore_from_environment():
    encoded_text = os.environ["PICKLE_PAYLOAD"]
    payload = encoded_text.encode("latin-1")
    return decode_pickle(payload)
