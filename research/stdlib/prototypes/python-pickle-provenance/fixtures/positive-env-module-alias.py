import os
import pickle as codec


def restore_from_environment():
    encoded_text = os.environ["PICKLE_PAYLOAD"]
    payload = encoded_text.encode("latin-1")
    return codec.loads(payload)
