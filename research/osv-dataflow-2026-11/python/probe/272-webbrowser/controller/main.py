import sys
import webbrowser


def show():
    return webbrowser.get().open(sys.argv[1])
