"""Research probe for BrokkAi/bifrost-packs#348: the `ok` case."""
import bz2


def f(chunk, next_chunk):
    """Exercise the f case."""
    dec = bz2.BZ2Decompressor()
    dec.decompress(chunk)
    return dec.decompress(next_chunk)
