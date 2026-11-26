import json
import re


def loads(text):
    # A local helper that shares the stdlib name but does not parse.
    return text.strip()


def strip_all(lines):
    return [loads(line) for line in lines]


def strip_each(lines):
    out = []
    for line in lines:
        out.append(loads(line))
    return out


def decode_once(blob, keys):
    # Parsed and compiled once, outside the loop.
    document = json.loads(blob)
    pattern = re.compile(r"^[a-z]+$")
    return [document[key] for key in keys if pattern.match(key)]


def compile_fixed():
    # A for-each loop over a small collection literal is excluded.
    patterns = []
    for text in ["a+", "b+", "c+"]:
        patterns.append(re.compile(text))
    return patterns
