"""Request values checked only by assert statements (BrokkAi/bifrost-packs#433)."""
from flask import Flask, request

app = Flask(__name__)

ALLOWED_FORMATS = {"csv", "json"}


@app.route("/export")
def export():
    """Check the export format with an assert."""
    fmt = request.args.get("format")
    assert fmt in ALLOWED_FORMATS
    return fmt


@app.route("/upload", methods=["POST"])
def upload():
    """Check the content length with an assert."""
    size = request.headers.get("Content-Length")
    assert size is not None and size.isdigit(), "missing length"
    return size


@app.route("/theme")
def theme():
    """Check a cookie inside the assert itself."""
    assert request.cookies.get("theme") != "", "empty theme"
    return "ok"


@app.route("/tags", methods=["POST"])
def tags():
    """Check the tag count with an assert."""
    names = request.form.getlist("tag")
    assert len(names) < 50
    return ",".join(names)
