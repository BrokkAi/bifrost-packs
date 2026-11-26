"""Request values parsed by parse_qs or parse_qsl without max_num_fields (BrokkAi/bifrost-packs#436)."""
import urllib.parse
from urllib.parse import parse_qs, parse_qsl

from flask import Flask, request

app = Flask(__name__)


@app.route("/oauth/callback")
def oauth_callback():
    """Parse an OAuth state parameter."""
    state = parse_qs(request.args.get("state"))
    return state.get("next", ["/"])[0]


@app.route("/prefs")
def prefs():
    """Parse preferences stored in a cookie."""
    pairs = urllib.parse.parse_qsl(request.cookies.get("prefs"), keep_blank_values=True)
    return dict(pairs)


@app.route("/forwarded")
def forwarded():
    """Parse the query string a proxy forwarded, with an explicit None cap."""
    original = request.headers.get("X-Original-Query")
    return parse_qs(original, max_num_fields=None)


@app.route("/batch", methods=["POST"])
def batch():
    """Parse batched operations with four positional arguments."""
    return parse_qsl(request.form.get("ops"), True, False, "utf-8")


@app.route("/legacy")
def legacy():
    """Parse with None passed as the sixth positional argument."""
    return parse_qs(request.args.get("q"), False, False, "utf-8", "replace", None)
