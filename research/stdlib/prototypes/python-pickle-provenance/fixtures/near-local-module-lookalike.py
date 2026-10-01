class LocalCodec:
    @staticmethod
    def loads(payload):
        return payload


pickle = LocalCodec()


def parse(payload):
    return pickle.loads(payload)
