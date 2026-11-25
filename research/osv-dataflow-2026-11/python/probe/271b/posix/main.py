import os
import posixpath


def show():
    template = os.environ["TEMPLATE"]
    return posixpath.expandvars(template)
