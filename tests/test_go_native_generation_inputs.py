"""Contract checks for the migrated Go os native-generation inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from scripts.content import read_lock


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "230019e376d5c1198b079482d4334ed2d18217ba"
BASE_JOBS = {
    "jdk21-result-use",
    "c-libc-result-use",
    "csharp-result-use",
    "php-result-use",
    "ruby-result-use",
    "javascript-string-result-use",
    "typescript-string-result-use",
    "python-str-result-use",
    "python-status-result-use",
    "python-performance-summaries",
}
RECIPES = {"jvm", "python", "php-builtin", "typescript", "rust"}
GO_NOTICE_PATH = "semantic-packs/go/notices/go-1.26.0-BSD-3-Clause.txt"
GO_NOTICE_SHA256 = "911f8f5782931320f5b8d1160a76365b83aea6447ee6c04fa6d5591467db9dad"
GO_INPUTS = {
    "go-stdlib-os-result-contracts": {
        "spec": "semantic-packs/go/go-stdlib-os-result-contracts.spec.json",
        "model": "semantic-packs/models/go-stdlib-os.json",
        "pack_id": "bifrost.go.stdlib.os",
        "payload_sha256": "e467f63e984dfc2f62196c209a59187e4da5982a286938dd7f121e700ee9c5b5",
    },
    "go-stdlib-os-declarations": {
        "spec": "semantic-packs/go/go-stdlib-os-declarations.spec.json",
        "model": "semantic-packs/models/go-stdlib-os-declarations.json",
        "pack_id": "bifrost.go.stdlib.os-declarations",
        "payload_sha256": "2cfaee35b9b4cb3f5685fa956282c7f2f4557fb2652046d8fb71b308674f5411",
    },
}


def _load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class GoNativeGenerationInputTests(unittest.TestCase):
    def test_two_go_models_are_explicit_jobs_and_existing_plan_is_preserved(self):
        config = _load("native-generation.json")
        jobs = {row["name"]: row for row in config["jobs"]}
        self.assertEqual(set(jobs), BASE_JOBS | set(GO_INPUTS))
        self.assertEqual({row["name"] for row in config["recipes"]}, RECIPES)
        self.assertEqual(len(config["jobs"]), 12)
        self.assertEqual(len(config["recipes"]), 5)

        for name, expected in GO_INPUTS.items():
            with self.subTest(job=name):
                job = jobs[name]
                self.assertEqual(job, {
                    "name": name,
                    "spec": expected["spec"],
                    "artifact": expected["model"],
                })
                spec = _load(expected["spec"])
                model_bytes = (ROOT / expected["model"]).read_bytes()
                model = json.loads(model_bytes)
                self.assertEqual(spec["pack_id"], expected["pack_id"])
                self.assertEqual(model["pack_id"], expected["pack_id"])
                self.assertEqual(model["schema_version"], 8)
                self.assertEqual(set(model["compatibility"]), {"toolchains"})
                self.assertEqual(spec["compatibility"], model["compatibility"])
                self.assertEqual(spec["activation"], model["shards"][0]["activation"])
                self.assertEqual(spec["provenance"], model["provenance"])
                self.assertEqual(spec["license"], "BSD-3-Clause")
                self.assertEqual(spec["license"], model["license"])
                self.assertEqual(spec["safety"], model["safety"])
                self.assertEqual(spec["artifact"]["sha256"], _sha256(model_bytes))
                self.assertEqual(
                    spec["artifact"]["url"],
                    f"https://github.com/BrokkAi/bifrost-packs/blob/{SOURCE_COMMIT}/{expected['model']}",
                )
                self.assertTrue(spec["measurement_queries"])
                canonical_payload = json.dumps(
                    model["shards"][0]["payload"], sort_keys=True, separators=(",", ":")
                ).encode()
                self.assertEqual(_sha256(canonical_payload), expected["payload_sha256"])

    def test_go_result_contract_and_declaration_lookup_anchors_are_real(self):
        result_spec = _load(GO_INPUTS["go-stdlib-os-result-contracts"]["spec"])
        result_model = _load(GO_INPUTS["go-stdlib-os-result-contracts"]["model"])
        self.assertEqual(result_spec["measurement_queries"], [{
            "kind": "procedure",
            "language": "go",
            "owner": "os",
            "name": "Create",
            "has_receiver": False,
            "parameter_count": 1,
        }])
        summaries = result_model["shards"][0]["payload"]["summaries"]
        by_id = {row["id"]: row for row in summaries}
        self.assertEqual(len(summaries), 10)
        self.assertEqual(len([row for row in summaries if row.get("result_contracts")]), 7)
        self.assertIn("os.create", by_id)
        self.assertEqual(by_id["os.create"]["target"]["symbol"], "os.Create(name string)")

        decl_spec = _load(GO_INPUTS["go-stdlib-os-declarations"]["spec"])
        decl_payload = _load(GO_INPUTS["go-stdlib-os-declarations"]["model"])["shards"][0]["payload"]
        self.assertEqual(decl_spec["measurement_queries"], [
            {"kind": "type", "name": "os.File"},
            {"kind": "member", "owner": "os.File", "name": "Close"},
        ])
        type_ids = {row["name"]: row["id"] for row in decl_payload["types"]}
        self.assertEqual(len(type_ids), 6)
        self.assertEqual(len(decl_payload["members"]), 21)
        self.assertIn("os.File", type_ids)
        self.assertIn({"name": "Close", "owner": type_ids["os.File"]}, [
            {"name": row["name"], "owner": row["owner"]}
            for row in decl_payload["members"]
        ])

    def test_new_spec_classification_is_public_and_license_matches(self):
        lock = read_lock(ROOT)
        entries = {row["path"]: row for row in lock["files"]}
        for expected in GO_INPUTS.values():
            row = entries[expected["spec"]]
            self.assertEqual(row["classification"], "public")
            self.assertEqual(row["license"], "BSD-3-Clause")
            self.assertEqual(row["source_path"], expected["spec"])
            self.assertEqual(row["sha256"], _sha256((ROOT / expected["spec"]).read_bytes()))

    def test_go_1260_license_notice_is_exact_and_referenced_by_both_specs(self):
        notice_bytes = (ROOT / GO_NOTICE_PATH).read_bytes()
        self.assertEqual(len(notice_bytes), 1453)
        self.assertEqual(_sha256(notice_bytes), GO_NOTICE_SHA256)
        for expected in GO_INPUTS.values():
            spec = _load(expected["spec"])
            self.assertEqual(spec["notices"], ["notices/go-1.26.0-BSD-3-Clause.txt"])

        lock = read_lock(ROOT)
        entries = {row["path"]: row for row in lock["files"]}
        self.assertEqual(entries[GO_NOTICE_PATH], {
            "path": GO_NOTICE_PATH,
            "source_path": GO_NOTICE_PATH,
            "sha256": GO_NOTICE_SHA256,
            "classification": "public",
            "license": "BSD-3-Clause",
        })


if __name__ == "__main__":
    unittest.main()
