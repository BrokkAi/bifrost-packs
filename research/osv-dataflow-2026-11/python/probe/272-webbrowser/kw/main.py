import sys
import webbrowser


def show():
    return webbrowser.open(sys.argv[1], new=2)
