import re
import sys


def inspect_regex():
    subject = sys.argv[1]
    re.search(r"^\s+|\s+$", subject)
    re.search(r"^\s+$", subject)
    pattern = re.compile(r"^\d+E?\d+$")
    pattern.search(subject)
