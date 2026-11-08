#!/usr/bin/env python3
"""Build the identifier typo table from two Apache-2.0 sources.

1. Apache OpenOffice's en-US AutoCorrect list:
   `main/extras/source/autotext/lang/en-US/acor_en-US.dat` from
   apache/openoffice at the pinned commit below, a zip archive whose
   `DocumentList.xml` maps typed misspellings to their corrections. Apache
   OpenOffice distributes it under the Apache License 2.0. The script refuses
   an input whose sha256 differs from the pin.
2. `tools/identifier-typos-supplement.txt`, a supplement authored by Brokk
   under Apache-2.0. Its header records how the entries were produced and the
   rule that keeps third-party lists out of it.

From both, only pairs of two different lower-case ASCII words are kept, and
misspellings of three letters or fewer are dropped (the engine never reports
such parts, as CodeQL's normalized_typos does not). From the AutoCorrect list,
the entries in REAL_WORDS are dropped as well: their "misspelling" is itself an
English word or name and would flag correct identifiers. `--word-list` checks
the supplement's misspellings against a permissively licensed English word
list and fails on any that is a word.

The output keeps the two sources in separate sections; a supplement pair the
AutoCorrect list already has appears only in the first. The script prints the
content hash the pack manifest pins.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

AOO_COMMIT = "17d397d7eb7e2935ed88d281ee3068516ad1cd47"
AOO_PATH = "main/extras/source/autotext/lang/en-US/acor_en-US.dat"
AOO_SHA256 = "6c33244af810e8b568a140b850283d828e2478240ba8ec8e1dec9a905c3ec400"
BLOCK_LIST = "{http://openoffice.org/2001/block-list}"
# AutoCorrect entries whose left side is a real word or name.
REAL_WORDS = {"directer", "directers", "herat", "stroy", "themself", "withe"}
SUPPLEMENT = Path(__file__).with_name("identifier-typos-supplement.txt")
WORD = re.compile(r"^[a-z]+$")
DIGEST_DOMAIN = b"bifrost-identifier-typos:v1\0"

HEADER = f"""\
# Known identifier misspellings for js/misspelled-identifier, one `wrong right`
# pair per line. Built by tools/aoo_autocorrect_typos.py from two sources, both
# under the Apache License, Version 2.0; see NOTICE.md.
#
# Only pairs of two different lower-case ASCII words are kept, and
# misspellings of three letters or fewer are removed.
"""

AOO_SECTION = f"""
# Section 1: Apache OpenOffice en-US AutoCorrect list
# {AOO_PATH}
# at apache/openoffice commit {AOO_COMMIT}.
# Copyright The Apache Software Foundation; portions copyright 2000-2011
# Oracle and/or its affiliates. A few entries whose misspelling is itself a
# word are removed.
"""

SUPPLEMENT_SECTION = """
# Section 2: supplement authored by Brokk, Apache-2.0
# (tools/identifier-typos-supplement.txt). Pairs already in section 1 are
# not repeated.
"""


def keep(wrong: str, right: str) -> bool:
    return bool(WORD.match(wrong) and WORD.match(right)) and wrong != right and len(wrong) > 3


def autocorrect_pairs(archive: bytes) -> set[tuple[str, str]]:
    with zipfile.ZipFile(io.BytesIO(archive)) as dat:
        root = ElementTree.fromstring(dat.read("DocumentList.xml"))
    pairs = set()
    for block in root.iter(f"{BLOCK_LIST}block"):
        wrong = block.get(f"{BLOCK_LIST}abbreviated-name", "").lower()
        right = block.get(f"{BLOCK_LIST}name", "").lower()
        if keep(wrong, right) and wrong not in REAL_WORDS:
            pairs.add((wrong, right))
    return pairs


def supplement_pairs(text: str) -> set[tuple[str, str]]:
    pairs = set()
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 2 or not keep(*fields):
            raise ValueError(f"{SUPPLEMENT}:{number}: not an admissible `wrong right` pair: {line!r}")
        pairs.add((fields[0], fields[1]))
    return pairs


def content_hash(pairs: set[tuple[str, str]]) -> str:
    digest = hashlib.sha256(DIGEST_DOMAIN)
    for wrong, right in sorted(pairs):
        digest.update(f"{wrong}\0{right}\n".encode("ascii"))
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acor_dat", type=Path, help=f"{AOO_PATH} at {AOO_COMMIT}")
    parser.add_argument("output", type=Path)
    parser.add_argument("--word-list", type=Path, help="English word list, one word per line")
    args = parser.parse_args(argv)
    archive = args.acor_dat.read_bytes()
    actual = hashlib.sha256(archive).hexdigest()
    if actual != AOO_SHA256:
        parser.error(f"{args.acor_dat} has sha256 {actual}, expected {AOO_SHA256}")
    autocorrect = autocorrect_pairs(archive)
    supplement = supplement_pairs(SUPPLEMENT.read_text(encoding="utf-8"))
    if args.word_list:
        words = {line.strip().lower() for line in args.word_list.read_text(encoding="utf-8", errors="replace").splitlines()}
        real = sorted(pair for pair in supplement if pair[0] in words)
        if real:
            parser.error(f"supplement misspellings that are words in {args.word_list}: {real}")
    extra = supplement - autocorrect
    body = (
        HEADER
        + AOO_SECTION
        + "".join(f"{wrong} {right}\n" for wrong, right in sorted(autocorrect))
        + SUPPLEMENT_SECTION
        + "".join(f"{wrong} {right}\n" for wrong, right in sorted(extra))
    )
    args.output.write_text(body, encoding="utf-8")
    print(content_hash(autocorrect | supplement))
    return 0


if __name__ == "__main__":
    sys.exit(main())
