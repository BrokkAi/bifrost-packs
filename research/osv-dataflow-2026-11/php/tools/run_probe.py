#!/usr/bin/env python3
"""Run every probe case with an exact Bifrost binary and print compact results.

usage: run_probe.py BIFROST_BINARY OUT_DIR [--production BUNDLE_DIR] [LEAD | LEAD/CASE ...]

Without --production, open packs are disabled and only the research model is
active. With --production, the packs bundle is supplied and a `.php-version`
file is written so `bifrost.php-builtin` activates; the research model's
declaration shard is then dropped so the only declarations are the production
pack's.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROBE = Path(__file__).resolve().parents[1] / "probe"


def summarize(report: dict) -> dict:
    """Reduce one policy report to its completion, findings and first diagnostics."""
    out = {}
    for run in report.get("runs", []):
        completion = run.get("completion", {})
        entry = {"completion": completion.get("type")}
        if completion.get("reasons"):
            entry["reasons"] = completion["reasons"]
        if completion.get("unavailable_capabilities"):
            entry["unavailable"] = [f'{c["label"]}: {c["reason"]}' for c in completion["unavailable_capabilities"]]
        found = []
        for finding in run.get("findings", []):
            loc = finding.get("primary") or {}
            name = Path(loc.get("path", "?")).name
            line = (loc.get("region") or {}).get("start_line")
            proof = (finding.get("proof") or {}).get("state")
            found.append(f'{name}:{line} {finding.get("certainty", {}).get("type")} {proof} {finding.get("completeness", {}).get("type")}')
        entry["findings"] = found
        diags = []
        for diag in run.get("diagnostics", [])[:4]:
            diags.append(str(diag.get("message") or diag)[:300])
        if diags:
            entry["diagnostics"] = diags
        out = entry
    return out


def main() -> int:
    """Run the selected probe cases and write one report per case plus summary.json."""
    args = sys.argv[1:]
    binary, out_dir = Path(args[0]).resolve(), Path(args[1]).resolve()
    bundle = None
    rest = args[2:]
    if rest[:1] == ["--production"]:
        bundle, rest = Path(rest[1]).resolve(), rest[2:]
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="php-osv-probe-", dir=out_dir))
    root = work / "probe"
    shutil.copytree(PROBE, root)
    env = dict(os.environ, BIFROST_WORKSPACE_SEMANTIC_MODELS="on", BIFROST_SEMANTIC_PACK_DOWNLOAD="off")
    if bundle:
        env["BIFROST_OPEN_SEMANTIC_PACK_BUNDLE"] = str(bundle)
        (root / ".php-version").write_text("8.3.0\n", encoding="utf-8")
        model_path = root / ".bifrost/semantic-models/bifrost.research.php-osv-dataflow-probe.json"
        model = json.loads(model_path.read_text(encoding="utf-8"))
        model["shards"] = [s for s in model["shards"] if s["payload"]["kind"] != "declaration_facts"]
        model_path.write_text(json.dumps(model, indent=1), encoding="utf-8")
    else:
        env["BIFROST_OPEN_PACKS_DISABLE"] = "1"
    selected = rest or sorted(p.stem for p in (root / ".bifrost/policies").glob("*.rqlp"))
    cases = []
    for item in selected:
        if "/" in item:
            cases.append(item)
        else:
            cases.extend(f"{item}/{d.name}" for d in sorted((root / item).iterdir()) if d.is_dir())
    results = {}
    for case in cases:
        lead = case.split("/")[0]
        cache = Path(tempfile.mkdtemp(prefix="cache-", dir=work))
        proc = subprocess.run(
            [str(binary), "--policy", "--no-builtin-policies", "--no-incremental", "--root", ".",
             "--format", "json", "--sources", case, "--policy-file", f".bifrost/policies/{lead}.rqlp"],
            cwd=root, env=dict(env, BIFROST_CACHE_ROOT=str(cache)), capture_output=True, text=True, timeout=600,
        )
        (out_dir / (case.replace("/", "__") + ".json")).write_text(proc.stdout, encoding="utf-8")
        try:
            entry = summarize(json.loads(proc.stdout))
        except json.JSONDecodeError:
            entry = {"error": proc.stderr[-500:]}
        entry["exit_code"] = proc.returncode
        results[case] = entry
        print(case, json.dumps(entry), flush=True)
    (out_dir / "summary.json").write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
