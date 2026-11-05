import sys
import webbrowser


def show():
    page = sys.argv[1]
    return webbrowser.open("https://docs.python.org/3/"), page
