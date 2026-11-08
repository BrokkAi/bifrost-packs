"""Pin the reviewed implicit-adjustment trust boundary, not runtime qualification."""
import hashlib
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

    def test_native_job_pins_reviewed_source_and_std_activation(self):
        spec = json.loads((ROOT / "semantic-packs/rust/rust-std-deref-summaries.spec.json").read_text())
        source = ROOT / "semantic-packs/rust/bifrost.rust-std-deref-summaries.json"
        std = json.loads((ROOT / "semantic-packs/rust/rust-stdlib-nightly-2026-08-24.json").read_text())
        self.assertEqual(spec["artifact"]["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(spec["kind"], {"artifact_kind": "authored_semantic_model"})
        self.assertEqual(spec["activation"], std["activation"])
        self.assertEqual(spec["measurement_activation"], std["measurement_activation"])
        self.assertTrue(spec["safety"]["review_required"])
        jobs = json.loads((ROOT / "native-generation.json").read_text())["jobs"]
        self.assertEqual([job for job in jobs if job["name"] == "rust-std-deref-summaries"], [{
            "name": "rust-std-deref-summaries",
            "spec": "semantic-packs/rust/rust-std-deref-summaries.spec.json",
            "artifact": "semantic-packs/rust/bifrost.rust-std-deref-summaries.json",
        }])
