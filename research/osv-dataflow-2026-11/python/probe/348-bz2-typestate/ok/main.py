import bz2


def f(chunk, next_chunk):
    dec = bz2.BZ2Decompressor()
    dec.decompress(chunk)
    return dec.decompress(next_chunk)
