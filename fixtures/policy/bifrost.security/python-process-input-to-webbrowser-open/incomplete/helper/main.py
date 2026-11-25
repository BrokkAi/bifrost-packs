import sys
import webbrowser

from links import normalize


def show_normalized():
    return webbrowser.open(normalize(sys.argv[1]))
