"""Pin the reviewed implicit-adjustment trust boundary, not runtime qualification."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RustStdDerefSummariesTests(unittest.TestCase):
    def test_only_exact_shared_std_deref_members_are_authorized(self):
        pack = json.loads((ROOT / "semantic-packs/rust/bifrost.rust-std-deref-summaries.json").read_text())
        std = json.loads((ROOT / "semantic-packs/rust/rust-stdlib-nightly-2026-08-24.json").read_text())
        self.assertTrue(pack["safety"]["review_required"])
        self.assertFalse(pack["safety"]["generated_code_only"])
        self.assertEqual(pack["compatibility"]["toolchains"], std["compatibility"]["toolchains"])
        self.assertEqual(pack["shards"][0]["activation"], std["activation"])
        self.assertEqual(len(pack["shards"]), 1)
        payload = pack["shards"][0]["payload"]
        self.assertEqual(payload["kind"], "procedure_summaries")
        summaries = payload["summaries"]
        self.assertEqual(len(summaries), 2)
        for summary, path, owner in zip(summaries, ["alloc.json", "std.json"], ["alloc.string.String", "std.path.PathBuf"]):
            with self.subTest(owner=owner):
                target = summary["target"]
                self.assertEqual(target["path"], path)
                self.assertTrue(target["symbol"].startswith(owner + ".deref#member."))
                self.assertEqual(len(target["symbol"].split(".trait.")[-1]), 64)
                self.assertTrue(target["has_receiver"])
                self.assertEqual(target["parameter_count"], 0)
                self.assertEqual(summary["completeness"], "complete")
                self.assertTrue(summary["ordinary_heap_unchanged"])
                self.assertTrue(summary["no_concurrency_effects"])
                self.assertEqual(summary["effects"], [])
                self.assertEqual(summary["transfers"], [{
                    "input": {"kind": "receiver"}, "exit_kind": "normal",
                    "output": {"kind": "normal_return"},
                    "value_transfer": {"kind": {"kind": "conversion", "preservation": "identity"},
                                       "operation": {"kind": "none"}},
                }])
