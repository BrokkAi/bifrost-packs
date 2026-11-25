#!/usr/bin/env python3
"""Replay the Java OSV data-flow probes against a Bifrost release binary.

Usage: BIFROST=/path/to/bifrost python3 -I research/osv-dataflow-2026-11/java/probe/run.py

Copies each probe root and the reviewed framework-decls models into a fresh
temporary directory and prints one JSON report: the dispatch outcome of every
JDK call in bind/Calls.java, the three research policy runs and the shipped
ObjectInputStream fixture runs. Nothing is compiled or executed.
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
REPO = HERE.parents[3]
EXPECTED_BUILD = "90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69"
DECLS = REPO / "semantic-packs/framework-decls"
MODELS = [
    DECLS / "bifrost.jdk-framework-decls.json",
    DECLS / "staged/bifrost.jdk-framework-summaries.json",
    DECLS / "staged/bifrost.javax.servlet-api-framework-decls.json",
    DECLS / "staged/bifrost.javax.servlet-api-summaries.json",
]
FIXTURE = REPO / "fixtures/policy/bifrost.security/java-objectinputstream-read-without-filter"
JDBC_RULE = REPO / "rules/bifrost.security/policies/jvm/servlet-parameter-to-jdbc.rqlp"
POLICY_PROBES = {
    "300-ldap": ".bifrost/policies/ldap-raw-filter.rqlp",
    "305-regex": ".bifrost/policies/request-regex.rqlp",
    "servlet-jdbc-baseline": ".bifrost/policies/servlet-parameter-to-jdbc.rqlp",
}


def bifrost(binary, root, *args):
    """Run Bifrost on root with a fresh cache and return its stdout."""
    with tempfile.TemporaryDirectory(prefix="bifrost-cache-") as cache:
        env = dict(
            os.environ,
            BIFROST_OPEN_PACKS_DISABLE="1",
            BIFROST_SEMANTIC_PACK_DOWNLOAD="off",
            BIFROST_WORKSPACE_SEMANTIC_MODELS="on",
            BIFROST_CACHE_DIR=cache,
        )
        done = subprocess.run(
            [binary, "--root", str(root), *args],
            capture_output=True, env=env, check=False, timeout=900,
        )
    return done.stdout


def dispatch_table(binary, root, path):
    """Return the dispatch outcome of every call in one probe file."""
    query = {
        "schema_version": "1", "languages": ["java"],
        "match": {"kind": "call"}, "steps": [{"op": "dispatch_outcome"}],
        "result_detail": "full", "limit": 300,
    }
    out = bifrost(binary, root, "--tool", "query_code", "--args", json.dumps(query))
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
    return sorted(rows, key=lambda r: (r["line"], r["call"]))


def policy_run(binary, root, sources, policy):
    """Run one policy and summarise its completion, findings and diagnostics."""
    out = bifrost(
        binary, root, "--policy", "--no-builtin-policies", "--no-incremental",
        "--sources", sources, "--format", "json", "--policy-file", policy,
    )
    run = json.loads(out)["runs"][0]
    return {
        "policy_hash": run["policy_hash"],
        "completion": run["completion"]["type"],
        "reasons": run["completion"].get("reasons", []),
        "findings": sorted(
            f'{f["primary"]["path"]}:{f["primary"]["region"]["start_line"]} '
            f'{f["certainty"]["type"]} {f["proof"]["state"]} {f["completeness"]["type"]}'
            for f in run["findings"]
        ),
        "diagnostics": sorted({d["message"][:240] for d in run["diagnostics"]}),
    }


def with_models(root):
    """Copy the reviewed framework-decls models into a probe root."""
    target = root / ".bifrost/semantic-models"
    target.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        shutil.copy(model, target / model.name)


def main():
    """Replay every probe in a temporary directory and print the report as JSON."""
    binary = os.environ.get("BIFROST", "bifrost")
    profile = subprocess.run([binary, "pack-engine-profile"], capture_output=True, text=True).stdout
    if EXPECTED_BUILD not in profile:
        sys.exit(f"expected Bifrost build {EXPECTED_BUILD}")
    report = {
        "build_identity": EXPECTED_BUILD,
        "binary_sha256": hashlib.sha256(Path(shutil.which(binary) or binary).read_bytes()).hexdigest(),
        "model_sha256": {m.name: hashlib.sha256(m.read_bytes()).hexdigest() for m in MODELS},
    }
    with tempfile.TemporaryDirectory(prefix="java-osv-dataflow-") as tmp:
        tmp = Path(tmp)
        bind = tmp / "bind-root"
        bind.mkdir()
        shutil.copytree(HERE / ".bifrost", bind / ".bifrost")
        shutil.copytree(HERE / "bind", bind / "bind")
        with_models(bind)
        report["dispatch"] = dispatch_table(binary, bind, "bind/Calls.java")
        report["policies"] = {}
        for name, policy in POLICY_PROBES.items():
            root = tmp / name
            shutil.copytree(HERE / name, root)
            with_models(root)
            if name == "servlet-jdbc-baseline":
                (root / ".bifrost/policies").mkdir(parents=True, exist_ok=True)
                shutil.copy(JDBC_RULE, root / policy)
            report["policies"][name] = policy_run(binary, root, "src", policy)
        fixture = tmp / "fixture"
        shutil.copytree(FIXTURE, fixture)
        policy = ".bifrost/policies/objectinputstream-read-without-filter.rqlp"
        report["objectinputstream_fixture"] = {
            "main": policy_run(binary, fixture, "src", policy),
            "incomplete": policy_run(binary, fixture / "incomplete", "src", policy),
        }
    json.dump(report, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
