"""Pin the Rust standard-library transfer summaries (source shape, not runtime qualification)."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "semantic-packs/rust-codeql-parity/bifrost.rust-std-transfers.json"
RESULT_OK_DECL = "member.593c436f45bdfb0723c1654b44557afc46096c2941607dcb171927fea64b05d9"
RESULT_OK_PATH = [{"variant": {"declaration": RESULT_OK_DECL}}, {"tuple": 0}]
CODEQL_REV = "1be292a1e54696ca543b4ad0f9b4537b9687caa7"


class RustStdTransfersTests(unittest.TestCase):
    """Verify the five reviewed Rust standard-library taint transfer summaries."""

    def setUp(self):
        self.pack = json.loads(PACK.read_text())
        self.assertEqual(len(self.pack["shards"]), 1)
        payload = self.pack["shards"][0]["payload"]
        self.assertEqual(payload["kind"], "procedure_summaries")
        self.summaries = {s["target"]["symbol"]: s for s in payload["summaries"]}

    def test_pack_metadata_and_provenance(self):
        self.assertEqual(self.pack["schema_version"], 35)
        self.assertEqual(self.pack["pack_id"], "bifrost.rust-std-transfers")
        self.assertEqual(self.pack["version"], "0.1.0")
        self.assertEqual(self.pack["language"], "rust")
        self.assertEqual(self.pack["ecosystem"], "cargo")
        self.assertEqual(self.pack["license"], "MIT")
        self.assertEqual(self.pack["completeness"], "complete")
        self.assertFalse(self.pack["safety"]["generated_code_only"])
        self.assertFalse(self.pack["safety"]["review_required"])
        self.assertEqual(self.pack["provenance"]["revision"], CODEQL_REV)
        source = self.pack["provenance"]["source"]
        for expected in (
            CODEQL_REV,
            "core.model.yml:131",
            "fs.model.yml:84",
            "rust.model.yml:4169,4172-4174",
            RESULT_OK_DECL,
        ):
            self.assertIn(expected, source)

    def test_exact_five_summaries_present_and_complete(self):
        self.assertEqual(
            set(self.summaries.keys()),
            {
                "core.result.Result.unwrap",
                "core.result.Result.unwrap_or",
                "core.result.Result.unwrap_or_default",
                "std.fs.Metadata.is_dir",
                "core.str.parse",
            },
        )
        for symbol, summary in self.summaries.items():
            with self.subTest(symbol=symbol):
                self.assertEqual(summary["completeness"], "complete")
                self.assertEqual(summary["effects"], [])
                self.assertTrue(summary["covers_overrides"])
                self.assertTrue(summary["target"]["has_receiver"])

    def test_str_parse_targets_result_ok_payload_only(self):
        parse = self.summaries["core.str.parse"]
        self.assertEqual(parse["target"], {
            "path": "library/core/src/str/mod.rs",
            "symbol": "core.str.parse",
            "has_receiver": True,
            "parameter_count": 0,
        })
        self.assertEqual(parse["transfers"], [{
            "input": {"kind": "receiver"},
            "exit_kind": "normal",
            "output": {"kind": "normal_return", "path": RESULT_OK_PATH},
        }])

    def test_result_unwrap_family_reads_ok_payload_only(self):
        unwrap = self.summaries["core.result.Result.unwrap"]
        self.assertEqual(unwrap["target"]["path"], "library/core/src/result.rs")
        self.assertEqual(unwrap["target"]["parameter_count"], 0)
        self.assertEqual(unwrap["transfers"], [{
            "input": {"kind": "receiver", "path": RESULT_OK_PATH},
            "exit_kind": "normal",
            "output": {"kind": "normal_return"},
        }])

        unwrap_or = self.summaries["core.result.Result.unwrap_or"]
        self.assertEqual(unwrap_or["target"]["path"], "library/core/src/result.rs")
        self.assertEqual(unwrap_or["target"]["parameter_count"], 1)
        self.assertEqual(unwrap_or["transfers"], [
            {
                "input": {"kind": "receiver", "path": RESULT_OK_PATH},
                "exit_kind": "normal",
                "output": {"kind": "normal_return"},
            },
            {
                "input": {"kind": "parameter", "ordinal": 0},
                "exit_kind": "normal",
                "output": {"kind": "normal_return"},
            },
        ])

        unwrap_or_default = self.summaries["core.result.Result.unwrap_or_default"]
        self.assertEqual(unwrap_or_default["target"]["path"], "library/core/src/result.rs")
        self.assertEqual(unwrap_or_default["target"]["parameter_count"], 0)
        self.assertEqual(unwrap_or_default["transfers"], [{
            "input": {"kind": "receiver", "path": RESULT_OK_PATH},
            "exit_kind": "normal",
            "output": {"kind": "normal_return"},
        }])

    def test_metadata_is_dir_summary(self):
        is_dir = self.summaries["std.fs.Metadata.is_dir"]
        self.assertEqual(is_dir["target"], {
            "path": "library/std/src/fs.rs",
            "symbol": "std.fs.Metadata.is_dir",
            "has_receiver": True,
            "parameter_count": 0,
        })
        self.assertEqual(is_dir["transfers"], [{
            "input": {"kind": "receiver"},
            "exit_kind": "normal",
            "output": {"kind": "normal_return"},
        }])

    def test_fixtures_exist(self):
        for rel in (
            "tests/cases/rust-std-transfers/README.md",
            "tests/cases/rust-std-transfers/parse-ok-positive/Cargo.toml",
            "tests/cases/rust-std-transfers/parse-ok-positive/src/lib.rs",
            "tests/cases/rust-std-transfers/parse-err-near-miss/Cargo.toml",
            "tests/cases/rust-std-transfers/parse-err-near-miss/src/lib.rs",
        ):
            self.assertTrue((ROOT / rel).is_file(), rel)


if __name__ == "__main__":
    unittest.main()
