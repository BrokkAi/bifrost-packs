#!/usr/bin/env python3
"""Replay the Kotlin/Scala JDK binding probe against a Bifrost binary.

Usage: BIFROST=/path/to/bifrost python3 -I research/kotlin-scala-jdk/probe/run.py

Copies the probe and the reviewed JDK declaration pack into a fresh temporary
root, then prints one JSON document with the per-call dispatch table, the
call-binding diagnostics and the three getenv-to-exec policy runs.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DECLS = REPO / "semantic-packs/framework-decls/bifrost.jdk-framework-decls.json"
EXPECTED_BUILD = "09a2503c5f7ced1630a9e3c445ead53dfc5925e8"
LANGS = {"java": "Calls.java", "kotlin": "Calls.kt", "scala": "Calls.scala"}
STDLIB = {"kotlin": "Stdlib.kt", "scala": "Stdlib.scala"}
ENV = dict(
    os.environ,
    BIFROST_OPEN_PACKS_DISABLE="1",
    BIFROST_SEMANTIC_PACK_DOWNLOAD="off",
    BIFROST_WORKSPACE_SEMANTIC_MODELS="on",
)


def bifrost(binary, root, *args):
    """Run Bifrost on root and return its exit code and stdout."""
    done = subprocess.run(
        [binary, "--root", str(root), *args],
        capture_output=True, env=ENV, check=False, timeout=600,
    )
    return done.returncode, done.stdout


def dispatch_table(binary, root, language, path):
    """Return the dispatch outcome of every call in one probe file."""
    query = {
        "schema_version": "1", "languages": [language],
        "match": {"kind": "call"}, "steps": [{"op": "dispatch_outcome"}],
        "result_detail": "full", "limit": 300,
    }
    _, out = bifrost(binary, root, "--tool", "query_code", "--args", json.dumps(query))
    lines = (root / path).read_text().split("\n")
    rows = []
    for row in json.loads(out)["structuredContent"]["results"]:
        if row.get("path") != path:
            continue
        span = row["range"]
        text = lines[span["start_line"] - 1]
        if span["start_line"] == span["end_line"]:
            text = text[span["start_column"] - 1:span["end_column"] - 1]
        rows.append({
            "line": span["start_line"], "call": text.strip()[:70],
            "outcome": row["outcome"], "coverage": row["coverage"],
            "targets": row["target_count"],
        })
    return rows


def binding_diagnostics(binary, root, language):
    """Return the distinct call-binding diagnostics for one language."""
    _, out = bifrost(binary, root, "--query-file", f"queries/call-bindings-{language}.rql")
    content = json.loads(out)["structuredContent"]
    return sorted({d["message"] for d in content.get("diagnostics", [])})


def policy_run(binary, root, language):
    """Run one getenv-to-exec probe policy and summarise its completion and findings."""
    code, out = bifrost(
        binary, root, "--policy", "--no-builtin-policies", "--no-incremental",
        "--sources", f"env/{language}", "--format", "json",
        "--policy-file", f".bifrost/policies/getenv-exec-{language}.rqlp",
    )
    run = json.loads(out)["runs"][0]
    return {
        "exit_code": code,
        "completion": run["completion"]["type"],
        "reasons": run["completion"].get("reasons", []),
        "findings": [
            {"certainty": f["certainty"]["type"], "proof": f["proof"]["state"],
             "completeness": f["completeness"]["type"]}
            for f in run["findings"]
        ],
    }


def main():
    """Replay the probe in a temporary root and print the report as JSON."""
    binary = os.environ.get("BIFROST", "bifrost")
    profile = subprocess.run([binary, "pack-engine-profile"], capture_output=True, text=True).stdout
    if EXPECTED_BUILD not in profile:
        sys.exit(f"expected Bifrost build {EXPECTED_BUILD}")
    with tempfile.TemporaryDirectory(prefix="kotlin-scala-jdk-") as tmp:
        root = Path(tmp) / "probe"
        shutil.copytree(HERE, root, ignore=shutil.ignore_patterns("run.py"))
        models = root / ".bifrost/semantic-models"
        models.mkdir(parents=True)
        shutil.copy(DECLS, models / DECLS.name)
        report = {
            "build_identity": EXPECTED_BUILD,
            "binary_sha256": hashlib.sha256(Path(shutil.which(binary) or binary).read_bytes()).hexdigest(),
            "jdk_framework_decls_sha256": hashlib.sha256(DECLS.read_bytes()).hexdigest(),
            "dispatch": {
                lang: dispatch_table(binary, root, lang, f"bind/{lang}/{name}")
                for lang, name in LANGS.items()
            },
            "stdlib_dispatch": {
                lang: dispatch_table(binary, root, lang, f"bind/{lang}/{name}")
                for lang, name in STDLIB.items()
            },
            "call_binding_diagnostics": {
                lang: binding_diagnostics(binary, root, lang) for lang in ("kotlin", "scala")
            },
            "getenv_exec": {lang: policy_run(binary, root, lang) for lang in LANGS},
        }
    json.dump(report, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
