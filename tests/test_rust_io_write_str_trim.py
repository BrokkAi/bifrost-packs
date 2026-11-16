"""Pin the str::trim member and summary in the io-write model (source shape, not runtime qualification)."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "semantic-packs/rust-codeql-parity/bifrost.rust-std-io-write.json"
TRIM = "std.primitive.str.trim"


class RustIoWriteStrTrimTests(unittest.TestCase):
    def setUp(self):
        self.pack = json.loads(PACK.read_text())
        self.members = self.pack["shards"][0]["payload"]["members"]
        self.summaries = self.pack["shards"][1]["payload"]["summaries"]

    def test_trim_member_is_a_str_method_returning_a_str_reference(self):
        members = [m for m in self.members if m["locator"]["symbol"] == TRIM]
        self.assertEqual(len(members), 1)
        member = members[0]
        self.assertEqual(member["id"], "member.rust-codeql.std-primitive-str-trim")
        self.assertEqual(member["owner"], "type.rust-codeql.std-primitive-str")
        self.assertEqual(member["name"], "trim")
        self.assertFalse(member["is_static"])
        self.assertEqual(member["locator"]["path"], "library/core/src/str/mod.rs")
        self.assertEqual(member["signature"], {
            "parameters": [],
            "returns": {"kind": "by_ref", "element": {"kind": "named", "name": "std.primitive.str"}},
        })

    def test_trim_summary_is_receiver_to_normal_return_only(self):
        summaries = [s for s in self.summaries if s["target"]["symbol"] == TRIM]
        self.assertEqual(len(summaries), 1)
        summary = summaries[0]
        self.assertEqual(summary["id"], "summary.rust-codeql.std-primitive-str-trim")
        self.assertEqual(summary["target"], {
            "path": "library/core/src/str/mod.rs", "symbol": TRIM,
            "has_receiver": True, "parameter_count": 0,
        })
        self.assertEqual(summary["completeness"], "complete")
        self.assertEqual(summary["effects"], [])
        self.assertEqual(summary["transfers"], [{
            "input": {"kind": "receiver"}, "exit_kind": "normal",
            "output": {"kind": "normal_return"},
        }])

    def test_no_scratch_ids_and_no_parse_summary(self):
        ids = [m["id"] for m in self.members] + [s["id"] for s in self.summaries]
        self.assertFalse([i for i in ids if "sensitive-scratch" in i])
        self.assertFalse([s for s in self.summaries if s["target"]["symbol"].endswith(".parse")])

    def test_version_and_provenance_cite_the_pinned_codeql_row(self):
        self.assertEqual(self.pack["version"], "0.6.0")
        self.assertIn("core.model.yml:132 at 1be292a1e54696ca543b4ad0f9b4537b9687caa7", self.pack["provenance"]["source"])

    def test_every_summary_targets_a_declared_member_and_ids_are_unique(self):
        symbols = {m["locator"]["symbol"] for m in self.members}
        symbols |= {alias for m in self.members for alias in m.get("aliases", [])}
        missing = [s["id"] for s in self.summaries if s["target"]["symbol"] not in symbols]
        self.assertEqual(missing, [])
        member_ids = [m["id"] for m in self.members]
        summary_ids = [s["id"] for s in self.summaries]
        self.assertEqual(len(member_ids), len(set(member_ids)))
        self.assertEqual(len(summary_ids), len(set(summary_ids)))


if __name__ == "__main__":
    unittest.main()
