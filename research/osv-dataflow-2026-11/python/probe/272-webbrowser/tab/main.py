import sys
import webbrowser


def show():
    return webbrowser.open_new_tab(sys.argv[1])
