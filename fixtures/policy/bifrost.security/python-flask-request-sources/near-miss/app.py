from urllib.request import urlopen

from flask import Flask, request
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)

DEFAULTS = ImmutableMultiDict([("status", "https://status.example.com/")])


@app.route("/status")
def status():
    # The request value is read but never reaches the URL.
    request.args.get("verbose")
    return urlopen("https://status.example.com/")


@app.route("/health")
def health():
    # An ImmutableMultiDict the application built is not request input.
    return urlopen(DEFAULTS.get("status"))
