"""Near misses for request values checked only by assert (BrokkAi/bifrost-packs#433)."""
from flask import Flask, abort, request

app = Flask(__name__)

ALLOWED_FORMATS = {"csv", "json"}


@app.route("/export")
def export():
    """Check the export format with an explicit abort."""
    fmt = request.args.get("format")
    if fmt not in ALLOWED_FORMATS:
        abort(400)
    return fmt


@app.route("/internal")
def internal():
    """Assert on a local constant."""
    limit = 50
    request.args.get("ignored")
    assert limit > 0
    return str(limit)


def page_size(default):
    """Check an internal invariant on a configured value."""
    assert isinstance(default, int)
    return default
