import os
from pathlib import Path


def ext_splitext(filename):
    return os.path.splitext(filename)[1]


def ext_suffix(filename):
    return Path(filename).suffix


def ext_rsplit(filename):
    return filename.rsplit(".", 1)[-1]


def ext_last(filename):
    return filename.split(".")[-1].lower()


def stem(filename):
    return filename.split(".")[0]


def minor_version(version):
    return version.split(".")[1]


def module_leaf(dotted_name):
    return dotted_name.split(".")[1]


def parts(filename):
    return filename.split(".")


def in_range(filename, lo, hi):
    return lo < len(filename.split(".")) < hi
