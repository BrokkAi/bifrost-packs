"""Pin the std lock-acquire summaries to the exact poison Mutex and RwLock members."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "semantic-packs/rust-std-sync/bifrost.rust-std-sync.json"
SPEC = ROOT / "semantic-packs/rust-std-sync/rust-std-sync.spec.json"
STD = ROOT / "semantic-packs/rust/rust-stdlib-nightly-2026-08-24.json"


class RustStdSyncTests(unittest.TestCase):
    def test_only_the_three_blocking_acquires_are_modeled(self):
        pack = json.loads(PACK.read_text())
        std = json.loads(STD.read_text())
        self.assertFalse(pack["safety"]["review_required"])
        self.assertFalse(pack["safety"]["generated_code_only"])
        self.assertEqual(pack["compatibility"]["toolchains"], std["compatibility"]["toolchains"])
        self.assertEqual(len(pack["shards"]), 1)
        self.assertEqual(pack["shards"][0]["activation"], std["activation"])
        payload = pack["shards"][0]["payload"]
        self.assertEqual(payload["kind"], "procedure_summaries")
        expected = [
            ("std.sync.poison.mutex.Mutex.lock#member.", "exclusive"),
            ("std.sync.poison.rwlock.RwLock.read#member.", "shared"),
            ("std.sync.poison.rwlock.RwLock.write#member.", "exclusive"),
        ]
        self.assertEqual(len(payload["summaries"]), len(expected))
        for summary, (prefix, mode) in zip(payload["summaries"], expected):
            with self.subTest(prefix=prefix):
                target = summary["target"]
                self.assertEqual(target["path"], "std.json")
                self.assertTrue(target["symbol"].startswith(prefix))
                self.assertEqual(len(target["symbol"].split("#member.")[1]), 64)
                self.assertTrue(target["has_receiver"])
                self.assertEqual(target["parameter_count"], 0)
                self.assertEqual(summary["completeness"], "complete")
                self.assertEqual(summary["transfers"], [])
                self.assertEqual(summary["concurrency_effects"],
                                 [{"kind": "lock_acquire", "lock": {"kind": "receiver"}, "mode": mode}])

    def test_native_job_pins_source_and_std_activation(self):
        spec = json.loads(SPEC.read_text())
        std = json.loads(STD.read_text())
        self.assertEqual(spec["artifact"]["sha256"], hashlib.sha256(PACK.read_bytes()).hexdigest())
        self.assertEqual(spec["kind"], {"artifact_kind": "authored_semantic_model"})
        self.assertEqual(spec["activation"], std["activation"])
        self.assertEqual(spec["measurement_activation"], std["measurement_activation"])
        self.assertFalse(spec["safety"]["review_required"])
        self.assertEqual(len(spec["measurement_queries"]), 3)
        jobs = json.loads((ROOT / "native-generation.json").read_text())["jobs"]
        self.assertEqual([job for job in jobs if job["name"] == "rust-std-sync"], [{
            "name": "rust-std-sync",
            "spec": "semantic-packs/rust-std-sync/rust-std-sync.spec.json",
            "artifact": "semantic-packs/rust-std-sync/bifrost.rust-std-sync.json",
        }])


if __name__ == "__main__":
    unittest.main()
