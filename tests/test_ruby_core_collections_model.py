"""Pin the draft Ruby core collection model (#385).

The model is not a native job yet: on Bifrost master it closes no element
access (BrokkAi/bifrost-dev#11874) and some summary shapes stop another Ruby
pack's summaries from applying (BrokkAi/bifrost-dev#11873). These checks keep
it out of the release recipe and pin its contracts until it is re-verified.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODEL = "semantic-packs/ruby/ruby-core-collections.json"


def _load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class RubyCoreCollectionsModelTests(unittest.TestCase):
    def test_model_is_not_a_native_job_yet(self):
        artifacts = {job["artifact"] for job in _load("native-generation.json")["jobs"]}
        self.assertNotIn(MODEL, artifacts)

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
        # dig calls `dig` on nested values, so it is not a pure accessor.
        members = {row["name"] for row in model["shards"][0]["payload"]["members"]}
        self.assertNotIn("dig", members)


if __name__ == "__main__":
    unittest.main()
