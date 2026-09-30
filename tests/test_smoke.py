import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.smoke import POLICY_ID, SmokeError, run_smoke


class SmokeHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        for path in (
            "rules/bifrost.code-smells/policies/dynamic-evaluation.rqlp",
            "rules/bifrost.code-smells/manifest.json",
            "tests/cases/dynamic-evaluation/positive.py",
            "tests/cases/dynamic-evaluation/near-miss.py",
        ):
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
        policy = self.repo / "rules/bifrost.code-smells/policies/dynamic-evaluation.rqlp"
        policy.write_text("(policy :id \"bifrost.correctness.dynamic-evaluation\")\n", encoding="utf-8")
        manifest = {
            "policies": [
                {
                    "path": "policies/dynamic-evaluation.rqlp",
                    "id": POLICY_ID,
                    "authored_hash": "4" * 64,
                }
            ]
        }
        (self.repo / "rules/bifrost.code-smells/manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (self.repo / "tests/cases/dynamic-evaluation/positive.py").write_text(
            "result = eval('1 + 1')\n", encoding="utf-8"
        )
        (self.repo / "tests/cases/dynamic-evaluation/near-miss.py").write_text(
            "import ast\nresult = ast.literal_eval('1')\n", encoding="utf-8"
        )
        self.fake_binary = self.root / "fake-bifrost"
        self._write_fake_binary()

    def _write_fake_binary(self, behavior="normal"):
        script = f'''#!/usr/bin/env python3
import json
import os
import pathlib
import sys

if "--version" in sys.argv:
    print("bifrost 9.8.7")
    raise SystemExit(0)

args = sys.argv[1:]
def arg(flag):
    return args[args.index(flag) + 1]

root = pathlib.Path(arg("--root"))
policy = pathlib.Path(arg("--policy-file"))
assert not policy.is_absolute()
assert policy.exists() and policy.parent == pathlib.Path(".")
assert "--no-builtin-policies" in args
assert os.environ.get("JAVA_HOME") == ""
assert os.environ.get("BIFROST_SEMANTIC_PACK_DOWNLOAD") == "off"
source = (root / "case.py").read_text()
positive = " = eval(" in source
findings = [{{"policy_id": "{POLICY_ID}", "primary": {{"path": "case.py"}}}}] if positive else []
run = {{"policy_id": "{POLICY_ID}", "policy_hash": "4444444444444444444444444444444444444444444444444444444444444444", "completion": {{"type": "complete"}}, "findings": findings, "diagnostics": []}}
report = {{"rules": [{{"policy_id": "{POLICY_ID}", "policy_hash": "4444444444444444444444444444444444444444444444444444444444444444"}}], "runs": [run], "diagnostics": []}}
behavior = {behavior!r}
if behavior == "malformed":
    pathlib.Path(arg("--output")).write_text("{{bad json")
elif behavior == "incomplete":
    run["completion"] = {{"type": "incomplete"}}
    pathlib.Path(arg("--output")).write_text(json.dumps(report))
else:
    pathlib.Path(arg("--output")).write_text(json.dumps(report))
raise SystemExit(1 if findings else 0)
'''
        self.fake_binary.write_text(script, encoding="utf-8")
        self.fake_binary.chmod(0o755)

    def test_smoke_records_binary_policy_fixtures_and_complete_1_0_runs(self):
        output = self.root / "evidence"
        result = run_smoke(self.fake_binary, output, repository_root=self.repo)

        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["engine_version"], "9.8.7")
        self.assertEqual(result["policy_authored_hash"], "4" * 64)
        self.assertEqual(
            result["binary_sha256"], hashlib.sha256(self.fake_binary.read_bytes()).hexdigest()
        )
        self.assertEqual([run["exit_code"] for run in result["runs"]], [1, 0])
        self.assertEqual([run["finding_count"] for run in result["runs"]], [1, 0])
        for run in result["runs"]:
            raw = json.loads((output / run["raw_report"]).read_text(encoding="utf-8"))
            self.assertEqual(raw["runs"][0]["completion"]["type"], "complete")
            self.assertTrue((output / run["stdout"]).is_file())
            self.assertTrue((output / run["stderr"]).is_file())
        self.assertIn("does not qualify the full copied content", result["scope"])

    def test_malformed_raw_report_fails_and_preserves_failure_evidence(self):
        self._write_fake_binary("malformed")
        output = self.root / "malformed-evidence"
        with self.assertRaisesRegex(SmokeError, "malformed"):
            run_smoke(self.fake_binary, output, repository_root=self.repo)
        summary = json.loads((output / "smoke.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["runs"][0]["status"], "failed")
        self.assertTrue((output / "runs/positive/raw-report.json").is_file())

    def test_incomplete_raw_report_is_never_counted_as_clean(self):
        self._write_fake_binary("incomplete")
        output = self.root / "incomplete-evidence"
        with self.assertRaisesRegex(SmokeError, "incomplete"):
            run_smoke(self.fake_binary, output, repository_root=self.repo)
        summary = json.loads((output / "smoke.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "failed")
        self.assertIsNone(summary["runs"][0]["finding_count"])


if __name__ == "__main__":
    unittest.main()
