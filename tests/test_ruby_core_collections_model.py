"""Pin the Ruby core collection model (#385).

On Bifrost master after BrokkAi/bifrost-dev#11873 and #11874 it closes
element access, `fetch` and `new` on literal and constructed Hash/Array
receivers, but not on untyped parameters, so it is not a native job yet.
These checks keep it out of the release recipe and pin its contracts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODEL = "semantic-packs/ruby/ruby-core-collections.json"


def _load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class RubyCoreCollectionsModelTests(unittest.TestCase):
    """Pin the draft model's contracts and its absence from the release recipe."""

    def test_model_is_not_a_native_job_yet(self):
        artifacts = {job["artifact"] for job in _load("native-generation.json")["jobs"]}
        self.assertNotIn(MODEL, artifacts)

    def test_identifiers_are_unique_across_shards(self):
        # A summary that reused a member id made discovery refuse the whole
        # workspace model directory (BrokkAi/bifrost-dev#11873).
        model = _load(MODEL)
        ids = [
            row["id"]
            for shard in model["shards"]
            for key in ("members", "summaries")
            for row in shard["payload"].get(key, [])
        ]
        self.assertEqual(len(ids), len(set(ids)), ids)

    def test_types_use_the_canonical_rubygems_identity(self):
        # The engine finds `Hash`/`Array` only by type_declaration_id(rubygems,
        # name); any other id leaves `Hash.new` results untyped, silently.
        def canonical(name: str) -> str:
            digest = hashlib.sha256()
            for value in (
                b"bifrost.external-declaration.type.v1",
                b"ecosystem",
                b"rubygems",
                b"name",
                name.encode(),
            ):
                digest.update(struct.pack(">Q", len(value)))
                digest.update(value)
            return "type." + digest.hexdigest()

        for row in _load(MODEL)["shards"][0]["payload"]["types"]:
            with self.subTest(type=row["name"]):
                self.assertEqual(row["id"], canonical(row["name"]))

    def test_summaries_have_no_effects_and_writes_reach_the_receiver(self):
        model = _load(MODEL)
        self.assertEqual(model["schema_version"], 8)
        self.assertFalse(model["safety"]["review_required"])
        summaries = {
            row["target"]["symbol"]: row
            for row in model["shards"][1]["payload"]["summaries"]
        }
        for symbol, row in summaries.items():
            with self.subTest(summary=symbol):
                self.assertEqual(row["completeness"], "complete")
                self.assertEqual(row["effects"], [])
                writes = "[]=" in symbol
                self.assertEqual(row["ordinary_heap_unchanged"], not writes)
                outputs = {transfer["output"]["kind"] for transfer in row["transfers"]}
                self.assertEqual("receiver" in outputs, writes)
                # `Array.new(array)` copies its argument's elements, so a
                # constructor that takes arguments must carry one to the result.
                if ".new" in symbol and row["target"]["parameter_count"] > 0:
                    self.assertIn("normal_return", outputs)
        # dig calls `dig` on nested values, so it is not a pure accessor.
        members = {row["name"] for row in model["shards"][0]["payload"]["members"]}
        self.assertNotIn("dig", members)


if __name__ == "__main__":
    unittest.main()
