import os
from urllib.request import urlopen

from flask import Flask, request

app = Flask(__name__)


@app.route("/ping")
def ping():
    host = request.args.get("host")
    return str(os.system("ping -c 1 " + host))


@app.route("/archive", methods=["POST"])
def archive():
    names = request.form.getlist("name")
    return str(os.system("tar czf out.tgz " + " ".join(names)))


@app.route("/greet")
def greet():
    agent = request.headers.get("User-Agent", "")
    return str(os.system("logger " + agent))


@app.route("/fetch")
def fetch():
    feed = request.cookies.get("feed")
    return urlopen(feed)


@app.route("/proxy")
def proxy():
    query = request.args
    target = query.get("url")
    return urlopen(target)
