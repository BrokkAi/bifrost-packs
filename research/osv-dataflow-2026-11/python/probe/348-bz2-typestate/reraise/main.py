"""Research probe for BrokkAi/bifrost-packs#348: the `reraise` case."""
import bz2


def f(chunk, next_chunk):
    """Exercise the f case."""
    dec = bz2.BZ2Decompressor()
    try:
        dec.decompress(chunk)
    except OSError:
        raise
    return dec.decompress(next_chunk)
