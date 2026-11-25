import os
import sys
import webbrowser
from webbrowser import open_new


def show_argument():
    return webbrowser.open(sys.argv[1])


def show_environment():
    link = os.environ["HELP_URL"]
    return open_new(link)


def show_new_tab():
    return webbrowser.open_new_tab(sys.argv[1])


def show_keyword_new():
    return webbrowser.open(sys.argv[1], new=2)


def show_positional_flags():
    return webbrowser.open(sys.argv[1], 2, False)


def show_constant():
    return webbrowser.open("https://docs.python.org/3/")


def show_constant_with_input():
    page = sys.argv[1]
    return webbrowser.open_new_tab("https://docs.python.org/3/"), page
