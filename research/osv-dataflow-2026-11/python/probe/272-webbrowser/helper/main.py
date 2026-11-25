import sys
import webbrowser

from links import normalize


def show():
    return webbrowser.open(normalize(sys.argv[1]))
