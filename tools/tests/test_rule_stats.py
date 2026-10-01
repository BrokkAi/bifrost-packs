import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools import rule_stats


POLICY = '''; (policy :id "decoy.comment")
(policy
  :schema-version 1
  :id "{rule_id}"
  :name "{name}"
  :severity warning
  :description "text containing :id fake and (language ruby), | [brackets]\\nsecond line"
  :tags [security "tag|pipe"]
  :analysis (analysis :type assertion
    :query (rql :schema-version 1
      (language {query_language} (call)))))
'''


class RuleStatsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "rules" / "family" / "policies").mkdir(parents=True)
        (self.root / "README.md").write_text(
            "# Fixture\n\n<!-- rule-stats:start -->\nold\n<!-- rule-stats:end -->\n\nKeep me.\n",
            encoding="utf-8",
        )
        (self.root / "docs").mkdir()
        self.write_policy()

    def write_policy(self, path="rules/family/policies/a.rqlp", **values):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        defaults = {"rule_id": "family.a", "name": "A policy | [with] newline\\nnext", "query_language": "cpp"}
        defaults.update(values)
        target.write_text(POLICY.format(**defaults), encoding="utf-8")
        return target

    def write_manifest(self, policies):
        manifest = {"schema_version": 2, "id": "family", "name": "Family", "policies": policies}
        path = self.root / "rules" / "family" / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path

    def test_parser_ignores_comments_and_strings_and_reads_real_language_operator(self):
        inventory = rule_stats.build_inventory(self.root)
        policy = inventory["policies"][0]
        self.assertEqual(policy["query_languages"], ["cpp"])
        self.assertEqual(policy["id"], "family.a")
        rendered = rule_stats.render_catalog(inventory)
        self.assertIn("Undeclared; query: cpp", rendered)
        self.assertIn("\\|", rendered)
        self.assertIn("\\[with\\]", rendered)
        self.assertNotIn("ruby", rendered)

    def test_language_pairs_overlap_and_paths_do_not_supply_support(self):
        second = self.write_policy(
            "rules/family/policies/b.rqlp",
            rule_id="family.b",
            name="B",
            query_language="c",
        )
        metadata = [
            {"path": "policies/a.rqlp", "id": "family.a", "category": "correctness", "supported_languages": ["c", "cpp"]},
            {"path": "policies/b.rqlp", "id": "family.b", "category": "security", "supported_languages": ["cpp"]},
        ]
        self.write_manifest(metadata)
        inventory = rule_stats.build_inventory(self.root)
        summary = inventory["summary"]
        self.assertEqual(summary["declared_language_policy_pair_count"], 3)
        self.assertEqual(summary["declared_language_count"], 2)
        self.assertEqual(summary["declared_language_policy_counts"], {"c": 1, "cpp": 2})
        self.assertIsNotNone(second)
        self.assertEqual(inventory["policies"][0]["supported_languages"], ["c", "cpp"])

    def test_missing_manifest_support_stays_unknown_and_duplicate_ids_fail(self):
        self.write_manifest([{"path": "policies/a.rqlp", "id": "family.a"}])
        inventory = rule_stats.build_inventory(self.root)
        self.assertIsNone(inventory["policies"][0]["supported_languages"])
        self.assertIn("Undeclared", rule_stats.render_catalog(inventory))
        self.write_policy("rules/family/policies/b.rqlp")
        self.write_manifest(
            [
                {"path": "policies/a.rqlp", "id": "family.a"},
                {"path": "policies/b.rqlp", "id": "family.a"},
            ]
        )
        with self.assertRaisesRegex(rule_stats.InventoryError, "duplicate rule ID"):
            rule_stats.build_inventory(self.root)

    def test_empty_support_differs_from_missing_and_empty_packs_count(self):
        self.write_manifest([{ "path": "policies/a.rqlp", "id": "family.a", "supported_languages": [] }])
        empty = self.root / "rules" / "empty" / "manifest.json"
        empty.parent.mkdir()
        empty.write_text(json.dumps({"schema_version": 2, "id": "empty", "policies": []}), encoding="utf-8")
        inventory = rule_stats.build_inventory(self.root)
        self.assertEqual(inventory["summary"]["pack_count"], 2)
        self.assertEqual(inventory["policies"][0]["supported_languages"], [])
        self.assertIn("None (empty declaration)", rule_stats.render_catalog(inventory))
        self.assertEqual(inventory["summary"]["declared_language_policy_pair_count"], 0)

    def test_manifest_id_and_policy_id_must_match(self):
        self.write_manifest([{"path": "policies/a.rqlp", "id": "other.id", "supported_languages": ["python"]}])
        with self.assertRaisesRegex(rule_stats.InventoryError, "does not match policy ID"):
            rule_stats.build_inventory(self.root)

    def test_malformed_and_duplicate_policy_fields_fail(self):
        policy = self.root / "rules/family/policies/a.rqlp"
        policy.write_text('(policy :schema-version 1 :id "a" :id "b" :name "A" :analysis (rql :schema-version 1))', encoding="utf-8")
        with self.assertRaisesRegex(rule_stats.InventoryError, "duplicate top-level field"):
            rule_stats.build_inventory(self.root)
        policy.write_text('(policy :schema-version 9 :id "a" :name "A" :analysis (rql :schema-version 1))', encoding="utf-8")
        with self.assertRaisesRegex(rule_stats.InventoryError, "unsupported policy schema"):
            rule_stats.build_inventory(self.root)
        policy.write_text('(not-policy :schema-version 1 :id "a" :name "A")', encoding="utf-8")
        with self.assertRaisesRegex(rule_stats.InventoryError, "root must be"):
            rule_stats.build_inventory(self.root)

    def test_case_expectations_count_declared_expected_findings_only(self):
        self.write_manifest([{"path": "policies/a.rqlp", "id": "family.a", "supported_languages": ["cpp"]}])
        fixture = self.root / "fixtures" / "sample.cpp"
        fixture.parent.mkdir()
        fixture.write_text("int x;\n", encoding="utf-8")
        case_dir = self.root / "tests" / "cases"
        case_dir.mkdir(parents=True)
        record = {
            "policy_path": "rules/family/policies/a.rqlp",
            "policy_id": "family.a",
            "cases": [
                {"fixture": "fixtures/sample.cpp", "expected_findings": [{"line": 1}]},
                {"fixture": "fixtures/sample.cpp", "expected_findings": []},
            ],
        }
        (case_dir / "a.json").write_text(json.dumps(record), encoding="utf-8")
        inventory = rule_stats.build_inventory(self.root)
        self.assertEqual(inventory["summary"]["case_expectation_count"], 2)
        self.assertEqual(inventory["policies"][0]["recorded_case_expectations"], {"positive": 1, "zero_expected": 1})
        self.assertIn("do not report runtime test results", rule_stats.render_catalog(inventory))
        record["policy_id"] = "other.id"
        (case_dir / "a.json").write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaisesRegex(rule_stats.InventoryError, "policy_id does not match"):
            rule_stats.build_inventory(self.root)

    def test_research_and_non_json_fixtures_do_not_enter_rule_inventory(self):
        research = self.root / "research" / "rules"
        research.mkdir(parents=True)
        (research / "ignored.rqlp").write_text("not a policy", encoding="utf-8")
        (self.root / "tests" / "cases").mkdir(parents=True)
        (self.root / "tests" / "cases" / "runner.py").write_text("{}", encoding="utf-8")
        self.assertEqual(rule_stats.build_inventory(self.root)["summary"]["policy_count"], 1)

    def test_write_changes_only_marked_readme_block_and_catalog(self):
        old_prefix = "# Fixture\n\n<!-- rule-stats:start -->\n"
        self.assertEqual(rule_stats.main(["--repo", str(self.root), "--write"]), 0)
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertTrue(readme.startswith(old_prefix))
        self.assertTrue(readme.endswith("\n\nKeep me.\n"))
        catalog = self.root / "docs" / "rule-catalog.md"
        self.assertTrue(catalog.exists())
        before = readme, catalog.read_text(encoding="utf-8")
        self.assertEqual(rule_stats.main(["--repo", str(self.root), "--check"]), 0)
        (self.root / "README.md").write_text(readme.replace("unique rules", "stale"), encoding="utf-8")
        stale_before = (self.root / "README.md").read_text(encoding="utf-8")
        error_output = io.StringIO()
        with contextlib.redirect_stderr(error_output):
            self.assertEqual(rule_stats.main(["--repo", str(self.root), "--check"]), 1)
        self.assertIn("stale", error_output.getvalue())
        self.assertEqual((self.root / "README.md").read_text(encoding="utf-8"), stale_before)
        self.assertEqual(catalog.read_text(encoding="utf-8"), before[1])

    def test_markers_required_and_json_is_deterministic(self):
        output_one = rule_stats.build_inventory(self.root)
        output_two = rule_stats.build_inventory(self.root)
        self.assertEqual(json.dumps(output_one, sort_keys=True), json.dumps(output_two, sort_keys=True))
        (self.root / "README.md").write_text("no marker\n", encoding="utf-8")
        error_output = io.StringIO()
        with contextlib.redirect_stderr(error_output):
            self.assertEqual(rule_stats.main(["--repo", str(self.root), "--write"]), 1)
        self.assertIn("marker", error_output.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(rule_stats.main(["--repo", str(self.root), "--check"]), 1)


if __name__ == "__main__":
    unittest.main()
