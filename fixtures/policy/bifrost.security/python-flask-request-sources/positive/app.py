from urllib.request import urlopen

from flask import Flask, request

app = Flask(__name__)


@app.route("/feed")
def feed():
    return urlopen(request.args.get("url"))


@app.route("/proxy")
def proxy():
    query = request.args
    target = query.get("target")
    return urlopen(target)


@app.route("/callback", methods=["POST"])
def callback():
    hooks = request.form.getlist("hook")
    return urlopen(hooks[0])


@app.route("/saved")
def saved():
    return urlopen(request.cookies.get("saved_url"))


@app.route("/upstream")
def upstream():
    return urlopen(request.headers.get("X-Upstream"))
