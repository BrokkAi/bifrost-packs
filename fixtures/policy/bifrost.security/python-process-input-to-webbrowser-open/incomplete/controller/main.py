import sys
import webbrowser


def show_with_controller():
    return webbrowser.get().open(sys.argv[1])
