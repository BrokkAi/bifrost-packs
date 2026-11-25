"""Near misses for request values parsed without max_num_fields (BrokkAi/bifrost-packs#436)."""
from urllib.parse import parse_qs, parse_qsl

from flask import Flask, request

app = Flask(__name__)

MAX_FIELDS = 100


@app.route("/oauth/callback")
def oauth_callback():
    state = parse_qs(request.args.get("state"), max_num_fields=20)
    return state.get("next", ["/"])[0]


@app.route("/prefs")
def prefs():
    return dict(parse_qsl(request.cookies.get("prefs"), True, False, "utf-8", "replace", MAX_FIELDS))


@app.route("/defaults")
def defaults():
    request.args.get("ignored")
    return parse_qs("page=1&size=20")


class Fields:
    """A local parser whose method shares the stdlib name."""

    def parse_qs(self, text):
        """Return the text unchanged."""
        return text


@app.route("/local")
def local():
    value = request.args.get("q")
    return Fields().parse_qs(value)
