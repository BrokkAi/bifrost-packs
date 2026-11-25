"""Near misses for request values inflated without an output bound (BrokkAi/bifrost-packs#435)."""
import base64
import zlib

from flask import Flask, request

app = Flask(__name__)

BUNDLED = zlib.compress(b"default settings")


@app.route("/defaults")
def defaults():
    request.args.get("ignored")
    return zlib.decompress(BUNDLED)


@app.route("/echo")
def echo():
    return base64.urlsafe_b64decode(request.cookies.get("state"))


class Codec:
    """A local codec whose method shares the stdlib name."""

    def decompress(self, data):
        """Return the data unchanged."""
        return data


@app.route("/local")
def local():
    value = request.args.get("blob")
    return Codec().decompress(value)
