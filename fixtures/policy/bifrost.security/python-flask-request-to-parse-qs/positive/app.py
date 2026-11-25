"""Request values parsed by parse_qs or parse_qsl without max_num_fields (BrokkAi/bifrost-packs#436)."""
import urllib.parse
from urllib.parse import parse_qs, parse_qsl

from flask import Flask, request

app = Flask(__name__)


@app.route("/oauth/callback")
def oauth_callback():
    state = parse_qs(request.args.get("state"))
    return state.get("next", ["/"])[0]


@app.route("/prefs")
def prefs():
    pairs = urllib.parse.parse_qsl(request.cookies.get("prefs"), keep_blank_values=True)
    return dict(pairs)


@app.route("/forwarded")
def forwarded():
    original = request.headers.get("X-Original-Query")
    return parse_qs(original, max_num_fields=None)


@app.route("/batch", methods=["POST"])
def batch():
    return parse_qsl(request.form.get("ops"), True, False, "utf-8")
