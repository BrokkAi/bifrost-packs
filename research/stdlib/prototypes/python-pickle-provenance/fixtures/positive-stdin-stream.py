import pickle as codec
import sys


def restore_from_stdin():
    stream = sys.stdin.buffer
    return codec.load(stream)
