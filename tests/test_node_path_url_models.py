"""Pin the Node path, url and zlib models and the JavaScript CVE-slice rules (#287, #291, #294, #478).

These checks pin source inputs only. Runtime behavior is recorded in the
fixture READMEs and research/osv-dataflow-2026-11/jsts/outcomes.json.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
NODE = ROOT / "semantic-packs" / "node"
FIXTURES = ROOT / "fixtures" / "policy" / "bifrost.security"
POLICIES = ROOT / "rules" / "bifrost.security" / "policies" / "javascript"
ACTIVATION = [
    {
        "package": {"name": "pkg:generic/nodejs.org/node@22.11.0"},
        "targets": [],
        "configurations": ["70db7f8c799decb554bc25e8bf410079c8b377f2852ee2a982d56db40f054056"],
        "artifact_sha256": "24e5130fa7bc1eaab218a0c9cb05e03168fa381bb9e3babddc6a11f655799222",
    }
]
MODULES = {
    "path": {
        "join": ["base", "segment"],
        "normalize": ["path"],
        "resolve": ["base", "segment"],
    },
    "url": {
        "parse": ["urlString"],
        "format": ["urlObject"],
    },
}
RULES = {
    "process-input-to-fs-write-path": {
        "lead": "BrokkAi/bifrost-packs#287 (CVE-2025-27210)",
        "fixture": "javascript-process-input-to-fs-write-path",
        "models": [
            NODE / "runtime-values/javascript/bifrost.node-runtime-values.json",
            NODE / "fs/javascript/bifrost.node-fs-javascript-declarations.json",
            NODE / "fs/javascript/bifrost.node-fs-javascript-summaries.json",
            NODE / "path/javascript/bifrost.node-path-javascript-declarations.json",
            NODE / "path/javascript/bifrost.node-path-javascript-summaries.json",
        ],
    },
    "process-input-to-fs-path": {
        "lead": "BrokkAi/bifrost-packs#393 (OpenSSF CVE Benchmark, path traversal)",
        "fixture": "javascript-process-input-to-fs-path",
        "models": [
            NODE / "runtime-values/javascript/bifrost.node-runtime-values.json",
            NODE / "fs/javascript/bifrost.node-fs-javascript-declarations.json",
            NODE / "fs/javascript/bifrost.node-fs-javascript-summaries.json",
            NODE / "path/javascript/bifrost.node-path-javascript-declarations.json",
            NODE / "path/javascript/bifrost.node-path-javascript-summaries.json",
        ],
    },
    "process-input-to-child-process-command": {
        "lead": "BrokkAi/bifrost-packs#393 (OpenSSF CVE Benchmark, command injection)",
        "fixture": "javascript-process-input-to-child-process-command",
        "workspaces": ("", "incomplete", "uncovered"),
        "models": [
            NODE / "runtime-values/javascript/bifrost.node-runtime-values.json",
            NODE / "child-process/javascript/bifrost.node-child-process-declarations.json",
            NODE / "child-process/javascript/bifrost.node-child-process-summaries.json",
        ],
    },
    "process-input-to-vm-code": {
        "lead": "BrokkAi/bifrost-packs#393 (OpenSSF CVE Benchmark, code injection)",
        "fixture": "javascript-process-input-to-vm-code",
        "models": [
            NODE / "runtime-values/javascript/bifrost.node-runtime-values.json",
            NODE / "vm/javascript/bifrost.node-vm-javascript-declarations.json",
        ],
    },
    "file-content-to-unbounded-decompression": {
        "lead": "BrokkAi/bifrost-packs#291 (CVE-2024-22025)",
        "fixture": "javascript-file-content-to-unbounded-decompression",
        "workspaces": ("", "incomplete", "uncovered"),
        "models": [
            NODE / "fs/javascript/bifrost.node-fs-javascript-declarations.json",
            NODE / "fs/javascript/bifrost.node-fs-javascript-summaries.json",
            NODE / "zlib/javascript/bifrost.node-zlib-javascript-declarations.json",
            NODE / "zlib/javascript/bifrost.node-zlib-javascript-summaries.json",
        ],
    },
    "process-input-to-fetch-url": {
        "lead": "BrokkAi/bifrost-packs#478 (CVE-2025-27152)",
        "fixture": "javascript-process-input-to-fetch-url",
        "workspaces": ("", "incomplete", "inline"),
        "models": [
            NODE / "runtime-values/javascript/bifrost.node-runtime-values.json",
            ROOT / "semantic-packs/web-network/javascript/bifrost.web-network-javascript.json",
        ],
    },
    "process-input-to-legacy-url-parse": {
        "lead": "BrokkAi/bifrost-packs#294 (CVE-2026-21712)",
        "fixture": "javascript-process-input-to-legacy-url-parse",
        "models": [
            NODE / "runtime-values/javascript/bifrost.node-runtime-values.json",
            NODE / "url/javascript/bifrost.node-url-javascript-declarations.json",
            NODE / "url/javascript/bifrost.node-url-javascript-summaries.json",
        ],
    },
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class NodePathUrlModelTests(unittest.TestCase):
    """Pin the path and url models, the fs summaries and the rule fixture copies."""

    def test_models_are_review_required_and_fixed_arity(self):
        for module, members in MODULES.items():
            for kind in ("declarations", "summaries"):
                model = _load(NODE / module / "javascript" / f"bifrost.node-{module}-javascript-{kind}.json")
                with self.subTest(module=module, kind=kind):
                    self.assertEqual(model["pack_id"], f"bifrost.node-{module}-javascript-{kind}")
                    self.assertEqual(model["schema_version"], 8)
                    self.assertEqual(model["provenance"]["revision"], "v22.11.0")
                    self.assertEqual(model["license"], "Apache-2.0")
                    self.assertTrue(model["safety"]["review_required"])
                    self.assertEqual([s["activation"] for s in model["shards"]], [ACTIVATION])
            payload = _load(NODE / module / "javascript" / f"bifrost.node-{module}-javascript-declarations.json")
            declared = {
                row["name"]: [p["name"] for p in row["signature"]["parameters"]]
                for row in payload["shards"][0]["payload"]["members"]
            }
            self.assertEqual(declared, members)
            summaries = _load(NODE / module / "javascript" / f"bifrost.node-{module}-javascript-summaries.json")
            for row in summaries["shards"][0]["payload"]["summaries"]:
                name = row["target"]["symbol"].split(".", 1)[1]
                with self.subTest(summary=row["id"]):
                    # Summaries can't reference a variadic tail (bifrost-dev#9985).
                    self.assertNotIn("variadic", row["target"])
                    self.assertEqual(row["target"]["parameter_count"], len(members[name]))
                    self.assertEqual(row["completeness"], "complete")
                    returned = {
                        t["input"]["ordinal"]
                        for t in row["transfers"]
                        if t["input"]["kind"] == "parameter" and t["output"]["kind"] == "normal_return"
                    }
                    self.assertEqual(returned, set(range(len(members[name]))))

    def test_fs_summaries_cover_every_sink_member(self):
        summaries = _load(NODE / "fs/javascript/bifrost.node-fs-javascript-summaries.json")
        self.assertEqual(summaries["version"], "0.3.0")
        rows = summaries["shards"][0]["payload"]["summaries"]
        symbols = {row["target"]["symbol"] for row in rows}
        self.assertEqual(symbols, {
            "fs.existsSync", "fs.writeFileSync", "fs.appendFileSync", "fs.openSync",
            "fs.statSync", "fs.lstatSync", "fs.accessSync", "fs.readFileSync",
            "fs.readFileSync(path, options)", "fs.readdirSync", "fs.unlinkSync",
            "fs.rmSync", "fs.rmSync(path, options)",
        })
        for row in rows:
            with self.subTest(summary=row["id"]):
                # No fs result is argument data.
                self.assertFalse([t for t in row["transfers"] if t["output"]["kind"] == "normal_return"])
                # Every argument can appear in a thrown error, except from existsSync.
                thrown = {t["input"]["ordinal"] for t in row["transfers"] if t["output"]["kind"] == "exceptional_return"}
                expected = set() if row["target"]["symbol"] == "fs.existsSync" else set(range(row["target"]["parameter_count"]))
                self.assertEqual(thrown, expected)

    def test_zlib_models_pair_each_sink_member_with_a_summary(self):
        names = ["gunzipSync", "inflateSync", "inflateRawSync", "unzipSync", "brotliDecompressSync"]
        declarations = _load(NODE / "zlib/javascript/bifrost.node-zlib-javascript-declarations.json")
        summaries = _load(NODE / "zlib/javascript/bifrost.node-zlib-javascript-summaries.json")
        for model in (declarations, summaries):
            self.assertEqual(model["provenance"]["revision"], "v22.11.0")
            self.assertFalse(model["safety"]["review_required"])
        members = declarations["shards"][0]["payload"]["members"]
        self.assertEqual(
            sorted((m["name"], len(m["signature"]["parameters"])) for m in members),
            sorted((n, a) for n in names for a in (1, 2)),
        )
        rows = summaries["shards"][0]["payload"]["summaries"]
        self.assertEqual(
            sorted((r["target"]["symbol"].split(".", 1)[1].split("(")[0], r["target"]["parameter_count"]) for r in rows),
            sorted((n, a) for n in names for a in (1, 2)),
        )
        for row in rows:
            with self.subTest(summary=row["id"]):
                self.assertEqual(row["completeness"], "complete")
                self.assertEqual(row["effects"], [])
                # The input buffer reaches the result, and so do the options:
                # a dictionary supplies output bytes and info wraps the result.
                returned = {t["input"].get("ordinal") for t in row["transfers"] if t["output"]["kind"] == "normal_return"}
                self.assertEqual(returned, set(range(row["target"]["parameter_count"])))
                thrown = {t["input"]["ordinal"] for t in row["transfers"] if t["output"]["kind"] == "exceptional_return"}
                self.assertEqual(thrown, set(range(row["target"]["parameter_count"])))

    def test_fetch_model_declares_both_arities_with_summaries(self):
        model = _load(ROOT / "semantic-packs/web-network/javascript/bifrost.web-network-javascript.json")
        self.assertEqual(model["version"], "1.1.0")
        members = model["shards"][0]["payload"]["members"]
        self.assertEqual(
            sorted((m["id"], len(m["signature"]["parameters"])) for m in members),
            [("member.web-network.javascript.global-this.fetch", 2),
             ("member.web-network.javascript.global-this.fetch-1", 1)],
        )
        rows = model["shards"][1]["payload"]["summaries"]
        self.assertEqual(sorted(r["target"]["parameter_count"] for r in rows), [1, 2])
        for row in rows:
            with self.subTest(summary=row["id"]):
                # Only the input reaches the returned promise; init never does.
                self.assertEqual(
                    [(t["input"]["ordinal"], t["output"]["kind"]) for t in row["transfers"]],
                    [(0, "normal_return")],
                )

    def test_rules_carry_lead_and_fixture_copies_match(self):
        manifest = {p["path"]: p for p in _load(ROOT / "rules/bifrost.security/manifest.json")["policies"]}
        for name, expected in RULES.items():
            policy = POLICIES / f"{name}.rqlp"
            text = policy.read_text(encoding="utf-8")
            entry = manifest[f"policies/javascript/{name}.rqlp"]
            with self.subTest(rule=name):
                self.assertTrue(text.startswith(f"; Lead: {expected['lead']}"))
                self.assertIn(":call-modeling (call-modeling :unmodeled require-model)", text)
                self.assertEqual(entry["id"], f"bifrost.security.javascript.{name}")
                self.assertEqual(entry["activation"], "opt-in")
                self.assertEqual(entry["supported_languages"], ["javascript"])
                for workspace in expected.get("workspaces", ("", "incomplete")):
                    root = FIXTURES / expected["fixture"] / workspace
                    self.assertEqual((root / ".bifrost/policies" / policy.name).read_bytes(), policy.read_bytes())
                    copies = sorted((root / ".bifrost/semantic-models").iterdir())
                    self.assertEqual([c.name for c in copies], sorted(m.name for m in expected["models"]))
                    for model in expected["models"]:
                        self.assertEqual((root / ".bifrost/semantic-models" / model.name).read_bytes(), model.read_bytes())
                    enabled = _load(root / ".bifrost/packs.json")["enable"]
                    self.assertEqual(sorted(enabled), sorted(_load(m)["pack_id"] for m in expected["models"]))


if __name__ == "__main__":
    unittest.main()
