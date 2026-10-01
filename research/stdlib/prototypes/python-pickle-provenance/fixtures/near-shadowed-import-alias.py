from pickle import loads as decode_pickle


def parse(payload):
    decode_pickle = lambda value: value
    return decode_pickle(payload)
