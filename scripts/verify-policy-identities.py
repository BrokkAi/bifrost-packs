#!/usr/bin/env python3
"""Check all locked policy identities with the pinned production authoring CLI."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "release-contract"))
from policy_identity import verify_policy_identities


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--engine-version", required=True)
    parser.add_argument("--build-identity", required=True)
    args = parser.parse_args()
    result = verify_policy_identities(
        args.root, args.binary, args.output, args.engine_version, args.build_identity
    )
    print(f"Verified {len(result['policies'])} public source authoring identities; behavior qualification is separate.")


if __name__ == "__main__":
    main()
