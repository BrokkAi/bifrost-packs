"""Near misses for request values inflated without an output bound (BrokkAi/bifrost-packs#435)."""
import base64
import zlib

from flask import Flask, request

app = Flask(__name__)

BUNDLED = zlib.compress(b"default settings")


@app.route("/defaults")
def defaults():
    """Inflate a bundled constant."""
    request.args.get("ignored")
    return zlib.decompress(BUNDLED)


@app.route("/echo")
def echo():
    """Decode a cookie without inflating it."""
    return base64.urlsafe_b64decode(request.cookies.get("state"))


class Codec:
    """A local codec whose method shares the stdlib name."""

    def decompress(self, data):
        """Return the data unchanged."""
        return data


@app.route("/local")
def local():
    """Pass a request value to the local lookalike."""
    value = request.args.get("blob")
    return Codec().decompress(value)
