import os
from webbrowser import open_new


def show():
    link = os.environ["LINK"]
    return open_new(link)
