import os
from urllib.request import urlopen

from flask import Flask, request
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)

DEFAULTS = ImmutableMultiDict([("status", "https://status.example.com/")])


class Settings:
    def get(self, key):
        return "uptime"


settings = Settings()


@app.route("/uptime")
def uptime():
    # The request value is read but never reaches the command.
    request.args.get("verbose")
    return str(os.system("uptime"))


@app.route("/status")
def status():
    # A same-named `get` on a workspace class is not a request read.
    return str(os.system(settings.get("command")))


@app.route("/health")
def health():
    # An ImmutableMultiDict the application built is not request input.
    return urlopen(DEFAULTS.get("status"))
