"""Request values checked only by assert statements (BrokkAi/bifrost-packs#433)."""
from flask import Flask, request

app = Flask(__name__)

ALLOWED_FORMATS = {"csv", "json"}


@app.route("/export")
def export():
    fmt = request.args.get("format")
    assert fmt in ALLOWED_FORMATS
    return fmt


@app.route("/upload", methods=["POST"])
def upload():
    size = request.headers.get("Content-Length")
    assert size is not None and size.isdigit(), "missing length"
    return size


@app.route("/theme")
def theme():
    assert request.cookies.get("theme") != "", "empty theme"
    return "ok"


@app.route("/tags", methods=["POST"])
def tags():
    names = request.form.getlist("tag")
    assert len(names) < 50
    return ",".join(names)
