"""Shadowed control: a module function named eval hides the builtin."""

import sys


def eval(text):
    return text


eval(sys.argv[1])
