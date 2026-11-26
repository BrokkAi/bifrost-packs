import os
import tempfile


def mktemp(suffix=""):
    # A local helper that shares the stdlib name but creates the file securely.
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path


def create_report_path():
    return mktemp(".csv")
