"""Research probe for BrokkAi/bifrost-packs#348: the `reuse` case."""
import bz2

failures = []


def f(chunk, next_chunk):
    """Exercise the f case."""
    dec = bz2.BZ2Decompressor()
    try:
        dec.decompress(chunk)
    except OSError as error:
        failures.append(error)
    return dec.decompress(next_chunk)
