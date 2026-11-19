import os
from urllib.request import urlopen

from flask import Flask, request

app = Flask(__name__)


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
    # The request value only selects between two constant URLs.
    if request.args.get("region") == "eu":
        return urlopen("https://eu.status.example.com/").read()
    return urlopen("https://status.example.com/").read()
