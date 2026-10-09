# Source: github/codeql/python/ql/test/query-tests/Security/CWE-730-PolynomialReDoS/test.py @ ae741615f3e178ce61289a651790dc67fcc18e19; MIT License, Copyright GitHub, Inc.
# The Flask request source was replaced with the public lane's stdlib source.
import re
import sys


def upstream_regex_sinks():
    text = sys.argv[1]
    re.sub(r"^\s+|\s+$", "", text)
    re.match(r"^0\.\d+E?\d+$", text)
