import os
import tempfile
from tempfile import mktemp


def create_names():
    tempfile.mktemp()
    mktemp()
    os.tempnam()
    os.tmpnam()
    tempfile.NamedTemporaryFile()
