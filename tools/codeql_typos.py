#!/usr/bin/env python3
"""Derive the identifier typo table from CodeQL's TypoDatabase.qll.

The input is `shared/typos/codeql/typos/TypoDatabase.qll` from github/codeql,
which CodeQL generated from Wikipedia's "Lists of common misspellings/For
machines" and distributes under CC BY-SA 3.0. The output is an adaptation of
that list and keeps its license; see NOTICE.md.

The derivation applies upstream's own `normalized_typos` filter from
`javascript/ql/src/Expressions/Misspelling.qll`: it drops the pairs upstream
treats as intentional and misspellings of three letters or fewer. It also
drops pairs that are not two lower-case ASCII words, which the Bifrost table
format does not admit. It prints the content hash the pack manifest pins.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# `whitelisted` in Misspelling.qll.
UPSTREAM_INTENTIONAL = {
    ("thru", "through"),
    ("cant", "cannot"),
    ("inbetween", "between"),
    ("strat", "start"),
}
PAIR = re.compile(r'wrong = "([^"]*)" and right = "([^"]*)"')
WORD = re.compile(r"^[a-z]+$")
DIGEST_DOMAIN = b"bifrost-identifier-typos:v1\0"

HEADER = """\
# Known identifier misspellings for js/misspelled-identifier, one `wrong right`
# pair per line.
#
# Derived by tools/codeql_typos.py from github/codeql
# shared/typos/codeql/typos/TypoDatabase.qll at commit {commit}, which CodeQL
# generated from https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines
# (with custom additions) on 2018-01-19. Text by Wikipedia contributors and
# GitHub, Inc.
#
# This file is licensed under the Creative Commons Attribution-ShareAlike 3.0
# Unported License (CC BY-SA 3.0), not under this repository's Apache-2.0
# license: https://creativecommons.org/licenses/by-sa/3.0/ and
# licenses/CC-BY-SA-3.0.txt. Changes from the source: pairs CodeQL treats as
# intentional and misspellings of three letters or fewer are removed, as
# CodeQL's normalized_typos does, and so is every pair that is not two
# lower-case ASCII words.
"""


def derive(source: str) -> list[tuple[str, str]]:
    pairs = set()
    for wrong, right in PAIR.findall(source):
        if (wrong, right) in UPSTREAM_INTENTIONAL or len(wrong) <= 3:
            continue
        if not WORD.match(wrong) or not WORD.match(right) or wrong == right:
            continue
        pairs.add((wrong, right))
    return sorted(pairs)


def content_hash(pairs: list[tuple[str, str]]) -> str:
    digest = hashlib.sha256(DIGEST_DOMAIN)
    for wrong, right in pairs:
        digest.update(f"{wrong}\0{right}\n".encode("ascii"))
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("typo_database", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--commit", required=True, help="github/codeql commit of the input")
    args = parser.parse_args(argv)
    pairs = derive(args.typo_database.read_text(encoding="utf-8"))
    body = "".join(f"{wrong} {right}\n" for wrong, right in pairs)
    args.output.write_text(HEADER.format(commit=args.commit) + body, encoding="utf-8")
    print(content_hash(pairs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
