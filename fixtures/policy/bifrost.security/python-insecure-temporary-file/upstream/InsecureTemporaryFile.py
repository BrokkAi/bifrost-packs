# Source: github/codeql/python/ql/test/query-tests/Security/CWE-377-InsecureTemporaryFile/InsecureTemporaryFile.py @ ae741615f3e178ce61289a651790dc67fcc18e19; MIT License, Copyright GitHub, Inc.
import os
from tempfile import mktemp


def upstream_insecure_names():
    filename = mktemp()
    filename = os.tempnam()
    filename = os.tmpnam()
    return filename
