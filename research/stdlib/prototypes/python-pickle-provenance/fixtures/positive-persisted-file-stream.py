import pickle as codec


def restore_persisted_record(path):
    with open(path, "rb") as stream:
        return codec.load(stream)
