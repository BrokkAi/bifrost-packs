#!/usr/bin/env python3
"""Replay the pinned Java Map keySet/get discovery and semantic probes."""

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile

EXPECTED_BINARY_SHA256 = "168cf91d61f7504fbabf77974bfe53cdcc6f41abfbb727b7b152db18a3c4b545"
DEFAULT_BINARY = "/Users/dave/Library/Caches/bifrost-agent/binaries/0.12.0/darwin-arm64/bifrost"
QUERY_NAMES = (
    "map-keyset-get-discovery.rql",
    "map-keyset-get-captured-discovery.rql",
    "map-get-call-bindings.rql",
    "map-keyset-call-bindings.rql",
    "map-keyset-get-bindings.rql",
    "map-keyset-get-keyset-receiver-bindings.rql",
    "map-keyset-get-value-reference-bindings.rql",
    "map-keyset-get-value-reference-occurrences.rql",
    "map-keyset-get-call-sites.rql",
    "map-keyset-get-positive-receiver-outcome.rql",
    "map-keyset-get-receiver-outcomes.rql",
    "map-keyset-get-positive-state-events.rql",
    "map-keyset-get-changed-key-state-events.rql",
    "map-keyset-get-mutation-state-events.rql",
    "map-keyset-get-callback-state-events.rql",
    "map-keyset-get-positive-flow-relations.rql",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_result(output, name):
    return json.loads((output / (name + ".json")).read_text())


def query_rows(output, name):
    payload = load_result(output, name)
    return payload.get("structuredContent", {}).get("results", [])


def query_diagnostics(output, name):
    return load_result(output, name).get("structuredContent", {}).get("diagnostics", [])


def occurrence_ast(row):
    if row.get("reached_from_ast_id"):
        return row.get("reached_from_ast_id")
    for provenance in row.get("provenance", []):
        for step in provenance.get("steps", []):
            if step.get("op") in ("occurrences", "occurrences_in"):
                return step.get("result", {}).get("ast_id")
    return None


def bindings_by_occurrence(output, name):
    result = {}
    for row in query_rows(output, name):
        ast_id = occurrence_ast(row)
        if ast_id:
            result[ast_id] = {
                "id": row.get("id"),
                "name": row.get("name"),
                "kind": row.get("kind"),
                "range": row.get("range"),
            }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bifrost", default=DEFAULT_BINARY)
    parser.add_argument("--expected-sha256", default=EXPECTED_BINARY_SHA256)
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    binary = pathlib.Path(args.bifrost).resolve()
    if not binary.is_file():
        raise SystemExit("Bifrost binary not found: " + str(binary))
    version = subprocess.run([str(binary), "--version"], check=True, capture_output=True, text=True).stdout.strip()
    actual_hash = digest(binary)
    if "0.12.0" not in version:
        raise SystemExit("expected Bifrost 0.12.0, got: " + version)
    if actual_hash != args.expected_sha256:
        raise SystemExit(
            "Bifrost SHA-256 mismatch: expected " + args.expected_sha256
            + ", got " + actual_hash
            + "; pass --expected-sha256 only when requalifying a different exact binary"
        )

    proto = pathlib.Path(__file__).resolve().parents[1]
    repo = proto.parents[3]
    output = pathlib.Path(args.output_dir).resolve() if args.output_dir else proto / "evidence" / "replay"
    output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="bifrost-map-keyset-") as temp:
        root = pathlib.Path(temp)
        shutil.copytree(proto / "fixtures", root / "fixtures")
        shutil.copytree(proto / "queries", root / "queries")
        shutil.copytree(proto / "rqlp", root / "rqlp")

        for query in QUERY_NAMES:
            name = pathlib.Path(query).stem
            proc = subprocess.run(
                [str(binary), "--root", str(root), "--query-file", "queries/" + query],
                capture_output=True,
                text=True,
            )
            (output / (name + ".json")).write_text(proc.stdout)
            (output / (name + ".stderr")).write_text(proc.stderr)
            if proc.returncode:
                raise SystemExit("query failed: " + query + "; see " + str(output / (name + ".stderr")))

        policy = subprocess.run(
            [
                str(binary), "--root", str(root), "--policy-file",
                "rqlp/map-keyset-get-discovery-only.rqlp",
                "--evaluation-date", "2026-10-01", "--format", "json",
            ],
            capture_output=True,
            text=True,
        )
        (output / "discovery-policy.json").write_text(policy.stdout)
        (output / "discovery-policy.stderr").write_text(policy.stderr)
        if policy.returncode:
            raise SystemExit("policy replay failed; see " + str(output / "discovery-policy.stderr"))

    get_receivers = bindings_by_occurrence(output, "map-keyset-get-bindings")
    keyset_receivers = bindings_by_occurrence(output, "map-keyset-get-keyset-receiver-bindings")
    value_reference_bindings = bindings_by_occurrence(output, "map-keyset-get-value-reference-bindings")
    value_reference_targets = {
        row.get("ast_id"): row
        for row in query_rows(output, "map-keyset-get-value-reference-occurrences")
        if row.get("ast_id")
    }

    binding_comparisons = []
    for match in query_rows(output, "map-keyset-get-captured-discovery"):
        captures = {item.get("name"): item for item in match.get("captures", [])}
        if not {"loop", "iteratedMap", "lookupMap", "lookupKey"} <= set(captures):
            continue
        loop = captures["loop"]
        iterated = keyset_receivers.get(captures["iteratedMap"].get("ast_id"))
        lookup_map = get_receivers.get(captures["lookupMap"].get("ast_id"))
        lookup_key = value_reference_bindings.get(captures["lookupKey"].get("ast_id"))
        lookup_key_occurrence = value_reference_targets.get(captures["lookupKey"].get("ast_id"))
        lexical_target = (lookup_key_occurrence or {}).get("target")
        stable_key_id = (
            (lookup_key or {}).get("id")
            or (lookup_key_occurrence or {}).get("target_id")
            or (lookup_key_occurrence or {}).get("binding_id")
        )
        target_range = (lexical_target or {}).get("range", {})
        loop_header_line = loop.get("range", {}).get("start_line")
        binding_comparisons.append({
            "loop": loop.get("range"),
            "lookup": captures.get("lookup", {}).get("range"),
            "iterated_map_binding": iterated,
            "lookup_map_binding": lookup_map,
            "lookup_key_binding": lookup_key,
            "lookup_key_occurrence_target": lexical_target,
            "lookup_key_stable_binding_id": stable_key_id,
            "lookup_key_binding_status": (
                "stable_binding_id_available" if stable_key_id
                else "lexical_target_without_stable_binding_id" if lexical_target
                else "occurrence_target_unavailable"
            ),
            "receiver_binding_ids_equal": bool(
                iterated and lookup_map and iterated.get("id") == lookup_map.get("id")
            ),
            "lookup_key_stable_binding_resolved_by_ast_id": bool(lookup_key),
            "lookup_key_lexical_target_is_loop_variable_at_header": bool(
                lexical_target
                and lexical_target.get("kind") == "enhanced_for_variable"
                and target_range.get("start_line") == loop_header_line
            ),
        })

    policy_report = load_result(output, "discovery-policy")
    policy_summary = []
    for run in policy_report.get("runs", []):
        policy_summary.append({
            "policy_id": run.get("policy_id"),
            "completion": run.get("completion"),
            "finding_count": len(run.get("findings", [])),
            "finding_lines": sorted({
                finding.get("primary", {}).get("region", {}).get("start_line")
                for finding in run.get("findings", [])
            }),
        })

    base = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "HEAD", "origin/main"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()

    get_rows = query_rows(output, "map-get-call-bindings")
    keyset_rows = query_rows(output, "map-keyset-call-bindings")

    def model_receivers(rows):
        result = {}
        for row in rows:
            if row.get("binding_kind") != "receiver":
                continue
            result[str(row.get("range", {}).get("start_line"))] = {
                key: row.get(key) for key in (
                    "model_id", "model_pack_version", "model_producer",
                    "model_completeness", "selector_exact", "dispatch_outcome",
                    "dispatch_coverage", "model_active_set_hash",
                    "model_activation_reason",
                )
            } | {"pack_id": row.get("pack_id")}
        return result

    model_file = repo / "semantic-packs/golden-core/bifrost.jdk-golden-summaries.json"
    model_doc = json.loads(model_file.read_text())
    golden_summaries = {}
    for shard in model_doc.get("shards", []):
        for summary in shard.get("payload", {}).get("summaries", []):
            symbol = summary.get("target", {}).get("symbol")
            if symbol in ("java.util.Map.get(java.lang.Object)", "java.util.Map.keySet()"):
                golden_summaries[symbol] = {
                    "id": summary.get("id"),
                    "completeness": summary.get("completeness"),
                    "effects": summary.get("effects"),
                    "path": summary.get("target", {}).get("path"),
                }

    inputs = {}
    for path in sorted(proto.rglob("*")):
        if path.is_file() and "evidence/replay" not in path.as_posix():
            inputs[path.relative_to(repo).as_posix()] = digest(path)

    probe_names = tuple(pathlib.Path(name).stem for name in QUERY_NAMES)
    receipt = {
        "schema_version": 1,
        "source_base_sha": base,
        "branch": subprocess.run(
            ["git", "-C", str(repo), "branch", "--show-current"],
            check=True, capture_output=True, text=True,
        ).stdout.strip(),
        "engine": {
            "version": version,
            "binary_path": str(binary),
            "expected_sha256": args.expected_sha256,
            "actual_sha256": actual_hash,
            "pin_matched": actual_hash == args.expected_sha256,
        },
        "fixture_query_and_policy_sha256": inputs,
        "generated_jdk_calls": {
            "Map.get": model_receivers(get_rows),
            "Map.keySet": model_receivers(keyset_rows),
            "golden_core_procedure_summaries": golden_summaries,
        },
        "binding_comparisons": binding_comparisons,
        "probes": {
            name: {
                "result_count": len(query_rows(output, name)),
                "diagnostics": query_diagnostics(output, name),
            }
            for name in probe_names
        },
        "discovery_policy": {
            "policy_hash": (policy_report.get("rules") or [{}])[0].get("policy_hash"),
            "runs": policy_summary,
        },
        "performance": {"profiled": False, "speedup_claim": None},
        "upstream_related": [
            "https://github.com/BrokkAi/bifrost-dev/issues/3811",
            "https://github.com/BrokkAi/bifrost-dev/issues/2444",
            "https://github.com/BrokkAi/bifrost-dev/issues/2445",
        ],
    }
    receipt["raw_output_sha256"] = {
        path.name: digest(path)
        for path in sorted(output.glob("*.json"))
        if path.name != "receipt.json"
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "receipt": str(output / "receipt.json"),
        "engine_sha256": actual_hash,
        "policy": policy_summary,
        "binding_comparisons": binding_comparisons,
    }, indent=2))


if __name__ == "__main__":
    main()
