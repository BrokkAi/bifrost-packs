#!/usr/bin/env python3
"""Check generated rule documentation against the Git index, without staging files."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    root_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=False,
    )
    if root_result.returncode:
        print(root_result.stderr.strip(), file=sys.stderr)
        return root_result.returncode
    root = Path(root_result.stdout.strip())
    with tempfile.TemporaryDirectory(prefix="bifrost-rule-stats-") as temporary:
        snapshot = Path(temporary)
        result = subprocess.run(
            ["git", "checkout-index", "--all", f"--prefix={snapshot}/"],
            cwd=root, check=False,
        )
        if result.returncode:
            return result.returncode
        generator = snapshot / "tools" / "rule_stats.py"
        if not generator.is_file():
            print("rule-stats: stage tools/rule_stats.py before checking the index", file=sys.stderr)
            return 1
        result = subprocess.run(
            [sys.executable, "-B", str(generator), "--repo", str(snapshot), "--check"],
            cwd=snapshot, check=False,
        )
        if result.returncode:
            print(
                "rule-stats: regenerate with python3 tools/rule_stats.py --write, "
                "then stage README.md and docs/rule-catalog.md with the intended rule changes",
                file=sys.stderr,
            )
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
