import bz2


def f(chunk, next_chunk):
    dec = bz2.BZ2Decompressor()
    try:
        dec.decompress(chunk)
    except OSError:
        dec = bz2.BZ2Decompressor()
    return dec.decompress(next_chunk)
