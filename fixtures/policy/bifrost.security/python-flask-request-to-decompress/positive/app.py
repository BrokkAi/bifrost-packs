"""Request values inflated by one-shot decompressors with no output bound (BrokkAi/bifrost-packs#435)."""
import base64
import bz2
import gzip
import zlib

from flask import Flask, request

app = Flask(__name__)


@app.route("/state")
def state():
    raw = base64.urlsafe_b64decode(request.cookies.get("state"))
    return zlib.decompress(raw)


@app.route("/report", methods=["POST"])
def report():
    return gzip.decompress(base64.b64decode(request.form.get("payload")))


@app.route("/archive")
def archive():
    blob = base64.standard_b64decode(request.args.get("blob"))
    return bz2.decompress(blob)


@app.route("/raw")
def raw_header():
    return zlib.decompress(request.headers.get("X-Compressed"), 31)
